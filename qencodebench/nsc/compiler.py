"""Deterministic reversible compiler: Boolean IR -> phase oracle.

Architecture: compile the IR bottom-up into a COMPUTE sub-circuit that
leaves the root predicate on a flag wire (atoms may borrow problem qubits
directly with a polarity, so trivial atoms cost no ancilla), apply the
phase on the root, then append compute.inverse() -- the mirror uncompute
is guaranteed by construction, eliminating the dominant failure classes
(C3 ancilla discipline, C4 gate structure, C7 API misuse) mechanically.

The compiler's semantics are tested to agree exactly with ir.evaluate on
all inputs (see tests/test_nsc.py), so a classically validated IR yields
a functionally correct oracle, up to qubit-budget fit.
"""

from __future__ import annotations

from qiskit import QuantumCircuit

from qencodebench.core.circuits import (
    flag_on_pattern, flag_colors_differ, flag_cell_differs_const,
    controlled_add_const, counter_width, phase_on_pattern,
)
from qencodebench.nsc.ir import IRError, validate_schema


class BudgetError(IRError):
    pass


class _Alloc:
    def __init__(self, ancillas: list[int]):
        self.free = list(ancillas)
        self.used = 0

    def take(self, k: int = 1) -> list[int]:
        if len(self.free) < k:
            raise BudgetError(
                f"ancilla budget exhausted (needed {k} more, "
                f"{self.used} already in use); restructure the IR to use "
                "fewer/nested flags")
        out, self.free = self.free[:k], self.free[k:]
        self.used += k
        return out


def _compile_flag(body: QuantumCircuit, expr: dict,
                  problem: list[int], alloc: _Alloc) -> tuple[int, bool]:
    """Returns (wire, inverted): predicate == (wire XOR inverted)."""
    op = expr["op"]
    if op == "bit":
        return problem[expr["i"]], expr["val"] == 0
    if op == "not":
        w, inv = _compile_flag(body, expr["arg"], problem, alloc)
        return w, not inv
    if op == "cells_differ":
        t = alloc.take()[0]
        a, b = expr["a"], expr["b"]
        flag_colors_differ(body, (problem[2 * a], problem[2 * a + 1]),
                           (problem[2 * b], problem[2 * b + 1]), t)
        return t, False
    if op == "cell_ne_const":
        t = alloc.take()[0]
        a = expr["a"]
        flag_cell_differs_const(body, (problem[2 * a], problem[2 * a + 1]),
                                expr["val"], t)
        return t, False
    if op == "linsum_cmp":
        terms, rhs, cmp_ = expr["terms"], expr["rhs"], expr["cmp"]
        total = sum(c for c, _ in terms)
        w = counter_width(total)
        reg = alloc.take(w)
        for coef, i in terms:
            controlled_add_const(body, [problem[i]], reg, coef)
        t = alloc.take()[0]
        matching = [v for v in range(total + 1)
                    if {"==": v == rhs, "!=": v != rhs,
                        "<=": v <= rhs, ">=": v >= rhs}[cmp_]]
        if len(matching) > total + 1 - len(matching):
            # flip the complement: fewer pattern flips, then invert
            for v in range(total + 1):
                if v not in matching:
                    flag_on_pattern(body, reg,
                                    [(v >> j) & 1 for j in range(w)], t)
            return t, True
        for v in matching:
            flag_on_pattern(body, reg, [(v >> j) & 1 for j in range(w)], t)
        return t, False
    if op in ("and", "or"):
        child = [_compile_flag(body, a, problem, alloc)
                 for a in expr["args"]]
        child, const = _dedupe_children(child, op)
        t = alloc.take()[0]
        if const is not None:              # contradiction folded away
            if const:
                body.x(t)
            return t, False
        if op == "and":
            # t ^= all children true
            flag_on_pattern(body, [w for w, _ in child],
                            [0 if inv else 1 for _, inv in child], t)
            return t, False
        # or: t ^= all children false, then inverted flag
        flag_on_pattern(body, [w for w, _ in child],
                        [1 if inv else 0 for _, inv in child], t)
        return t, True
    raise IRError(f"unknown op {op!r}")


def _flatten(expr: dict) -> dict:
    """Normalization: and(and(a,b),c) == and(a,b,c); ditto for or; also
    collapses not(not(e)).  Models frequently emit nested groupings, and
    the flat form compiles with strictly fewer flag ancillas."""
    op = expr.get("op")
    if op in ("and", "or"):
        args = []
        for a in expr["args"]:
            fa = _flatten(a)
            if fa.get("op") == op:
                args.extend(fa["args"])
            else:
                args.append(fa)
        return {"op": op, "args": args}
    if op == "not":
        inner = _flatten(expr["arg"])
        if inner.get("op") == "not":
            return inner["arg"]
        return {"op": "not", "arg": inner}
    return expr


def _dedupe_children(child: list, mode: str):
    """Collapse duplicate (wire, inv) children; detect contradictions.
    Returns (children, constant) where constant is None or the boolean
    value the whole node folds to."""
    seen, out = {}, []
    for w, inv in child:
        if w in seen:
            if seen[w] != inv:            # same wire, both polarities
                return out, (mode == "or")
            continue                       # identical duplicate
        seen[w] = inv
        out.append((w, inv))
    return out, None


def _try_plan(fn):
    try:
        return fn()
    except BudgetError:
        return None


def build_into(qc: QuantumCircuit, problem_qubits: list[int],
               ancilla_qubits: list[int], ir: dict) -> None:
    """The build_oracle body: compute -> phase -> mirror uncompute.

    For a top-level AND four plans are tried in order of gate economy:
      A. per-child flags + one multi-controlled phase across them;
      B. like A but a single linsum child keeps its raw sum register and
         the phase enumerates its matching values (saves cmp+root flags);
      C. rolling counter: children are computed into ONE shared flag,
         counted, and uncomputed one at a time (ancilla reuse for tight
         T3-style budgets), phase on count == len(children);
      D. rolling counter + raw linsum register (B and C combined -- the
         zero-slack T3p budgets need both tricks at once).
    A top-level OR additionally gets the rolling plan in OR mode
    (phase on count >= 1).  Anything else falls back to the generic
    single-flag path.
    """
    validate_schema(ir, len(problem_qubits))
    ir = _flatten(ir)
    # normalize: a non-AND root becomes a single-child AND so every root
    # benefits from the phase-level plans (a bare linsum '== T' then
    # compiles with zero comparison flags via plan B)
    root_ir = ir if ir.get("op") == "and" else {"op": "and", "args": [ir]}
    attempts = [
        lambda: _plan_flags(qc, problem_qubits, ancilla_qubits, root_ir),
        lambda: _plan_linsum_enum(qc, problem_qubits, ancilla_qubits,
                                  root_ir),
        lambda: _plan_rolling(qc, problem_qubits, ancilla_qubits, root_ir),
        lambda: _plan_rolling_linsum(qc, problem_qubits, ancilla_qubits,
                                     root_ir),
    ]
    if ir.get("op") == "or":
        attempts.append(lambda: _plan_rolling(qc, problem_qubits,
                                              ancilla_qubits, ir))
    for attempt in attempts:
        if _try_plan(attempt):
            return
    raise BudgetError(
        "no compilation plan fits the ancilla budget; restructure "
        "the IR (fewer parallel constraints, or nested ORs)")


def _plan_flags(qc, problem, ancillas, ir) -> bool:
    """Plan A: every child gets a flag; one phase across all of them."""
    body = QuantumCircuit(qc.num_qubits)
    alloc = _Alloc(ancillas)
    child = [_compile_flag(body, a, problem, alloc) for a in ir["args"]]
    child, const = _dedupe_children(child, "and")
    qc.compose(body, inplace=True)
    if const is None:
        phase_on_pattern(qc, [w for w, _ in child],
                         [0 if inv else 1 for _, inv in child])
    elif const:                             # constant-true root: mark all
        qc.global_phase += 3.14159265358979323846
    qc.compose(body.inverse(), inplace=True)
    return True


def _plan_linsum_enum(qc, problem, ancillas, ir) -> bool:
    """Plan B: one linsum child stays as a raw register; the final phase
    enumerates its matching values alongside the other children's flags."""
    linsums = [a for a in ir["args"] if a.get("op") == "linsum_cmp"]
    if len(linsums) != 1:
        raise BudgetError("plan B needs exactly one linsum child")
    ls = linsums[0]
    others = [a for a in ir["args"] if a is not ls]
    body = QuantumCircuit(qc.num_qubits)
    alloc = _Alloc(ancillas)
    child = [_compile_flag(body, a, problem, alloc) for a in others]
    child, const = _dedupe_children(child, "and")
    if const is False:      # contradictory AND: oracle marks nothing
        qc.compose(body, inplace=True)
        qc.compose(body.inverse(), inplace=True)
        return True
    total = sum(c for c, _ in ls["terms"])
    w = counter_width(total)
    reg = alloc.take(w)
    for coef, i in ls["terms"]:
        controlled_add_const(body, [problem[i]], reg, coef)
    matching = [v for v in range(total + 1)
                if {"==": v == ls["rhs"], "!=": v != ls["rhs"],
                    "<=": v <= ls["rhs"], ">=": v >= ls["rhs"]}[ls["cmp"]]]
    qc.compose(body, inplace=True)
    for v in matching:
        phase_on_pattern(
            qc, [wq for wq, _ in child] + reg,
            [0 if inv else 1 for _, inv in child]
            + [(v >> j) & 1 for j in range(w)])
    qc.compose(body.inverse(), inplace=True)
    return True


def _rolling_child_body(qc, problem, flag, a) -> QuantumCircuit:
    """Compile one child into the shared flag (BudgetError if it needs
    more than the single flag ancilla)."""
    b = QuantumCircuit(qc.num_qubits)
    wire, inv = _compile_flag(b, a, problem, _Alloc([flag]))
    if wire != flag:                          # raw problem-qubit atom
        b.cx(wire, flag)
        if inv:
            b.x(flag)
    elif inv:
        b.x(flag)
    return b


def _roll_count(qc, bodies, flag, counter, phase_values, w,
                extra_wires=(), extra_bits_of=None):
    """Shared rolling core: count child truths, apply one phase per value
    in phase_values (optionally joined with extra register patterns),
    mirror-uncompute."""
    from qencodebench.core.circuits import (
        controlled_increment, controlled_decrement,
    )
    for b in bodies:
        qc.compose(b, inplace=True)
        controlled_increment(qc, [flag], counter)
        qc.compose(b.inverse(), inplace=True)
    for v in phase_values:
        if extra_bits_of is None:
            phase_on_pattern(qc, counter, [(v >> j) & 1 for j in range(w)])
        else:
            cnt, ext = v
            phase_on_pattern(
                qc, counter + list(extra_wires),
                [(cnt >> j) & 1 for j in range(w)] + extra_bits_of(ext))
    for b in reversed(bodies):
        qc.compose(b, inplace=True)
        controlled_decrement(qc, [flag], counter)
        qc.compose(b.inverse(), inplace=True)


def _plan_rolling(qc, problem, ancillas, ir) -> bool:
    """Plan C: compute each child into ONE shared flag, count it, then
    uncompute the child -- ancilla reuse for tight budgets.  AND roots
    phase on count == len(children); OR roots on every count >= 1."""
    args = ir["args"]
    w = counter_width(len(args))
    if len(ancillas) < 1 + w:
        raise BudgetError("rolling plan needs 1 + counter width ancillas")
    flag, counter = ancillas[0], list(ancillas[1:1 + w])
    bodies = [_rolling_child_body(qc, problem, flag, a) for a in args]
    n = len(args)
    values = [n] if ir["op"] == "and" else list(range(1, n + 1))
    _roll_count(qc, bodies, flag, counter, values, w)
    return True


def _plan_rolling_linsum(qc, problem, ancillas, ir) -> bool:
    """Plan D: plans B and C combined -- roll the non-linsum children
    through the shared flag into a counter, keep the single linsum child
    as a raw sum register, and let the final phases enumerate
    (count == all children) x (sum value satisfying the comparison)."""
    linsums = [a for a in ir["args"] if a.get("op") == "linsum_cmp"]
    if len(linsums) != 1:
        raise BudgetError("plan D needs exactly one linsum child")
    ls = linsums[0]
    others = [a for a in ir["args"] if a is not ls]
    if not others:
        raise BudgetError("bare linsum is plan B's job")
    m = len(others)
    w_c = counter_width(m)
    total = sum(c for c, _ in ls["terms"])
    w_s = counter_width(total)
    if len(ancillas) < 1 + w_c + w_s:
        raise BudgetError("plan D needs 1 + count + sum register ancillas")
    flag = ancillas[0]
    counter = list(ancillas[1:1 + w_c])
    reg = list(ancillas[1 + w_c:1 + w_c + w_s])

    bodies = [_rolling_child_body(qc, problem, flag, a) for a in others]
    sum_body = QuantumCircuit(qc.num_qubits)
    for coef, i in ls["terms"]:
        controlled_add_const(sum_body, [problem[i]], reg, coef)
    matching = [v for v in range(total + 1)
                if {"==": v == ls["rhs"], "!=": v != ls["rhs"],
                    "<=": v <= ls["rhs"], ">=": v >= ls["rhs"]}[ls["cmp"]]]

    qc.compose(sum_body, inplace=True)
    _roll_count(qc, bodies, flag, counter,
                [(m, v) for v in matching], w_c,
                extra_wires=reg,
                extra_bits_of=lambda v: [(v >> j) & 1 for j in range(w_s)])
    qc.compose(sum_body.inverse(), inplace=True)
    return True


def emit_build_oracle_code(ir: dict) -> str:
    """Self-contained candidate code for the standard L1-L4 pipeline."""
    import json
    return (
        "from qencodebench.nsc.compiler import build_into\n\n"
        f"IR = {json.dumps(ir)}\n\n"
        "def build_oracle(qc, problem_qubits, ancilla_qubits):\n"
        "    build_into(qc, problem_qubits, ancilla_qubits, IR)\n"
    )
