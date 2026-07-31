"""Per-constraint unit-verified agent.

The model still writes gates -- one fragment per constraint:

    def build_constraint_j(qc, problem_qubits, flag, scratch):
        # flag ^= 1  iff constraint j is satisfied
        # any scratch qubits used MUST be returned to |0>

The harness then
  1. UNIT-VERIFIES each fragment with a single simulation (uniform input):
     flag must equal the constraint predicate for every basis state, with
     no phase decoration, no leakage, scratch restored -- and failures get
     LOCAL feedback ("constraint 3: on x=5 flag should be 1, got 0"),
     fixing the credit-assignment problem of whole-oracle repair;
  2. ASSEMBLES the verified fragments deterministically (per-flag MCZ, or
     a rolling counter under tight budgets) with mirror uncompute by
     construction.

Between NSC (model writes no gates) and plain repair (global feedback),
this rung measures how much LOCALITY the model needs to write gates
correctly.
"""

from __future__ import annotations

import re

import numpy as np
from qiskit import QuantumCircuit

from qencodebench.core.circuits import (
    phase_on_pattern, controlled_increment, controlled_decrement,
    counter_width,
)
from qencodebench.core.sim import run_statevector
from qencodebench.core.task import TaskInstance
from qencodebench.verifier.diagnosis import constraint_predicates

MAX_FRAGMENT_ROUNDS = 2
UNIT_TOL = 1e-6

UNIT_PROMPT = '''\
You are writing a Grover phase oracle CONSTRAINT BY CONSTRAINT.  For each
numbered constraint below, write one Python/Qiskit function:

```python
def build_constraint_<j>(qc, problem_qubits, flag, scratch):
    ...
```

Contract for every fragment (checked individually by a simulator):
- After the fragment runs on a computational basis state, qubit `flag`
  must be flipped iff constraint j is SATISFIED (flag ^= predicate).
- The fragment must be purely classical-reversible: no phase decoration
  (no z/p/cz gates that leave phases), no measurement/reset.
- `scratch` is a list of helper qubits; any you use MUST be returned to
  |0> before the fragment ends (compute -> use -> uncompute).
- Only touch problem_qubits, flag, and scratch.

Write ALL fragments in ONE ```python code block (imports allowed:
qiskit, numpy, math).  Do NOT write the final phase or combine the
fragments -- the harness assembles them.

## Worked fragment example (a different constraint: "bits 0,1 not both 1")

```python
def build_constraint_1(qc, problem_qubits, flag, scratch):
    # satisfied iff NOT (b0 AND b1): flip flag when both are 1, then invert
    qc.ccx(problem_qubits[0], problem_qubits[1], flag)
    qc.x(flag)
```

## Problem

{problem}

## Constraints to implement (one fragment per line)

{constraints}
'''

FRAGMENT_FEEDBACK = '''
These fragments FAILED their unit checks; rewrite ONLY these functions
(reply with one ```python block containing just the corrected functions):

{reports}
'''


# ---------------------------------------------------------------------------
# unit verification
# ---------------------------------------------------------------------------

def unit_verify(fn, pred, n: int, total: int, flag: int,
                scratch: list[int]) -> tuple[bool, str, set[int]]:
    """One simulation: fragment must map |x>|0...> -> |x>|pred(x)>|0...>
    with a uniform global phase.  Returns (ok, report, touched_scratch)."""
    assert flag not in scratch and flag >= n, \
        "bench wiring error: flag must be disjoint from scratch/problem"
    sub = QuantumCircuit(total)
    try:
        fn(sub, list(range(n)), flag, scratch)
    except Exception as e:
        return False, f"raises {type(e).__name__}: {e}", set()
    touched = {sub.find_bit(q).index for ci in sub.data for q in ci.qubits}
    illegal = touched - set(range(n)) - {flag} - set(scratch)
    if illegal:
        return False, f"touches forbidden qubits {sorted(illegal)}", set()
    from qencodebench.verifier.verify import forbidden_instruction
    bad_op = forbidden_instruction(sub)
    if bad_op is not None:
        return False, (f"uses forbidden non-unitary instruction "
                       f"'{bad_op}' (fragments must be reversible)"), set()
    prep = QuantumCircuit(total)
    prep.h(range(n))
    prep.compose(sub, inplace=True)
    try:
        sv = run_statevector(prep)
    except Exception as e:
        return False, f"simulation failed: {e}", set()
    dim = 1 << n
    amp = 2 ** (-n / 2)
    expect_idx = {x + ((1 << flag) if pred(x) else 0) for x in range(dim)}
    scratch_mask = sum(1 << s for s in scratch)
    leak_idx = [i for i in range(len(sv))
                if i not in expect_idx and abs(sv[i]) ** 2 > 1e-9]
    if any(i & scratch_mask for i in leak_idx):
        leak = sum(abs(sv[i]) ** 2 for i in leak_idx)
        return False, ("  scratch qubits left dirty on some inputs "
                       f"(leaked weight {leak:.2e}); mirror-uncompute "
                       "your scratch work"), touched & set(scratch)
    bad = []
    ref_phase = None
    for x in range(dim):
        want = x + ((1 << flag) if pred(x) else 0)
        a = sv[want]
        if abs(abs(a) - amp) > UNIT_TOL:
            bad.append((x, f"flag should be {int(bool(pred(x)))}"
                           if abs(a) < amp / 2 else "amplitude corrupted"))
        else:
            if ref_phase is None:
                ref_phase = a
            elif abs(a / ref_phase - 1) > 10 * UNIT_TOL:
                bad.append((x, "phase decoration (fragment must be "
                               "classical-reversible, no z/p/cz)"))
        if len(bad) >= 4:
            break
    if bad:
        lines = []
        for x, why in bad[:4]:
            bits = ", ".join(f"q{i}={(x >> i) & 1}" for i in range(n))
            lines.append(f"  on x={x} ({bits}): {why}")
        return False, "\n".join(lines), touched & set(scratch)
    if leak_idx:                       # flag-side leakage without scratch
        leak = sum(abs(sv[i]) ** 2 for i in leak_idx)
        return False, (f"  leakage off the expected subspace "
                       f"({leak:.2e})"), touched & set(scratch)
    # fingerprint pass: distinct random magnitudes force the IDENTITY
    # mapping on the problem register -- a pred-preserving permutation
    # (e.g. an un-uncomputed helper CX between problem qubits) passes the
    # uniform screen above but scrambles the magnitude assignment
    rng = np.random.default_rng(0xF7A6)
    c = rng.uniform(0.5, 1.5, dim) * np.exp(
        1j * rng.uniform(0, 2 * np.pi, dim))
    c /= np.linalg.norm(c)
    init = np.zeros(1 << total, dtype=complex)
    init[:dim] = c
    out2 = run_statevector(sub, initial=init)
    ratio_ref = None
    for x in range(dim):
        want = x + ((1 << flag) if pred(x) else 0)
        r = out2[want] / c[x]
        if abs(abs(r) - 1.0) > 10 * UNIT_TOL:
            bits = ", ".join(f"q{i}={(x >> i) & 1}" for i in range(n))
            return False, (f"  on x={x} ({bits}): the fragment does not "
                           "map |x> back to |x> itself (it permutes or "
                           "fails to restore problem qubits)"), \
                touched & set(scratch)
        if ratio_ref is None:
            ratio_ref = r
        elif abs(r - ratio_ref) > 10 * UNIT_TOL:
            return False, ("  input-dependent phase detected on the "
                           "fingerprint state (fragment must be "
                           "classical-reversible)"), touched & set(scratch)
    return True, "", touched & set(scratch)


# ---------------------------------------------------------------------------
# deterministic assembly (emitted-code compatible)
# ---------------------------------------------------------------------------

def assemble_into(qc: QuantumCircuit, problem_qubits: list[int],
                  ancilla_qubits: list[int], fragments_src,
                  n_constraints: int, aggregator: str,
                  scratch_need: int) -> None:
    """fragments_src: single source str, or {str(j): block} mapping each
    fragment to ITS OWN source block -- executed in isolated namespaces so
    a stale block can never shadow a repaired function (the exact state
    the unit checks verified)."""
    if isinstance(fragments_src, dict):
        fns = []
        for j in range(n_constraints):
            ns_j: dict = {}
            exec(compile(fragments_src[str(j)], "<fragment>", "exec"), ns_j)
            fns.append(ns_j[f"build_constraint_{j + 1}"])
    else:
        ns: dict = {}
        exec(compile(fragments_src, "<fragments>", "exec"), ns)
        fns = [ns[f"build_constraint_{j + 1}"] for j in range(n_constraints)]
    m = n_constraints
    total = qc.num_qubits

    def frag(j, flag, scratch):
        sub = QuantumCircuit(total)
        fns[j](sub, problem_qubits, flag, scratch)
        return sub

    if len(ancilla_qubits) >= m + scratch_need:      # plan A: per-flag
        flags = ancilla_qubits[:m]
        scratch = ancilla_qubits[m:]
        subs = [frag(j, flags[j], scratch) for j in range(m)]
        for s in subs:
            qc.compose(s, inplace=True)
        if aggregator == "and":
            phase_on_pattern(qc, flags, [1] * m)
        else:
            qc.global_phase += np.pi
            phase_on_pattern(qc, flags, [0] * m)
        for s in reversed(subs):
            qc.compose(s.inverse(), inplace=True)
        return
    # plan C: rolling counter (ancilla reuse)
    w = counter_width(m)
    if len(ancilla_qubits) >= 1 + w + scratch_need:
        flag = ancilla_qubits[0]
        counter = ancilla_qubits[1:1 + w]
        scratch = ancilla_qubits[1 + w:]
        subs = [frag(j, flag, scratch) for j in range(m)]
        for s in subs:
            qc.compose(s, inplace=True)
            controlled_increment(qc, [flag], counter)
            qc.compose(s.inverse(), inplace=True)
        if aggregator == "and":
            phase_on_pattern(qc, counter, [(m >> i) & 1 for i in range(w)])
        else:
            for v in range(1, m + 1):
                phase_on_pattern(qc, counter,
                                 [(v >> i) & 1 for i in range(w)])
        for s in reversed(subs):
            qc.compose(s, inplace=True)
            controlled_decrement(qc, [flag], counter)
            qc.compose(s.inverse(), inplace=True)
        return
    # plan C2: hold-out rolling -- roll the first m-1 fragments, keep the
    # LAST one computed through the phase.  Covers zero-slack budgets
    # where counting to m needs one more counter bit than counting to m-1
    # (e.g. vertex_cover T3p with E = 2^k - 1 edges).
    w2 = counter_width(m - 1) if m > 1 else 0
    if m > 1 and len(ancilla_qubits) >= 1 + w2 + scratch_need:
        flag = ancilla_qubits[0]
        counter = ancilla_qubits[1:1 + w2]
        scratch = ancilla_qubits[1 + w2:]
        subs = [frag(j, flag, scratch) for j in range(m)]
        for s in subs[:-1]:
            qc.compose(s, inplace=True)
            controlled_increment(qc, [flag], counter)
            qc.compose(s.inverse(), inplace=True)
        qc.compose(subs[-1], inplace=True)
        if aggregator == "and":
            phase_on_pattern(
                qc, counter + [flag],
                [((m - 1) >> i) & 1 for i in range(w2)] + [1])
        else:
            # f = (count >= 1) OR flag: one phase per non-zero count value
            # (flag-independent), plus the (count == 0, flag == 1) corner
            for v in range(1, m):
                phase_on_pattern(qc, counter,
                                 [(v >> i) & 1 for i in range(w2)])
            phase_on_pattern(qc, counter + [flag], [0] * w2 + [1])
        qc.compose(subs[-1].inverse(), inplace=True)
        for s in reversed(subs[:-1]):
            qc.compose(s, inplace=True)
            controlled_decrement(qc, [flag], counter)
            qc.compose(s.inverse(), inplace=True)
        return
    raise RuntimeError(
        f"budget: need {1 + w2 + scratch_need} ancillas "
        f"(hold-out rolling plan), have {len(ancilla_qubits)}")


def emit_build_oracle_code(fragments_src, n_constraints: int,
                           aggregator: str, scratch_need: int) -> str:
    return (
        "from qencodebench.agent.unit_agent import assemble_into\n\n"
        f"FRAGMENTS_SRC = {fragments_src!r}\n\n"
        "def build_oracle(qc, problem_qubits, ancilla_qubits):\n"
        f"    assemble_into(qc, problem_qubits, ancilla_qubits, "
        f"FRAGMENTS_SRC, {n_constraints}, {aggregator!r}, {scratch_need})\n"
    )


# ---------------------------------------------------------------------------
# agent driver
# ---------------------------------------------------------------------------

def _extract_fragments(text: str) -> str | None:
    blocks = re.findall(r"```(?:python|py)?\s*\n(.*?)```", text, re.DOTALL)
    picked = [b for b in blocks if "def build_constraint_" in b]
    return "\n\n".join(picked) if picked else None


SELF_ASSEMBLY_NOTE = '''
Additionally, in the same code block, define
`def build_oracle(qc, problem_qubits, ancilla_qubits)` that allocates
flag qubits from ancilla_qubits, calls your fragments to compute them,
applies the phase for the combined predicate, and uncomputes everything
so all ancillas end in |0>.  Your build_oracle will be used directly.
'''


def run_unit_agent_sample(client, inst: TaskInstance, solutions: set[int],
                          temperature: float = 0.7,
                          options: dict | None = None) -> dict:
    """Ablation switches via ``options``:
      max_fragment_rounds (int, default 2)  -- 0 = no unit-feedback loop
      feedback_granularity ("full"|"which_only") -- which_only drops the
          per-input details, reporting only WHICH fragment failed
      self_assembly (bool) -- the model writes build_oracle itself
          (isolates the harness's mirror-assembly contribution)
    """
    opt = {"max_fragment_rounds": MAX_FRAGMENT_ROUNDS,
           "feedback_granularity": "full",
           "self_assembly": False, **(options or {})}
    agg, preds = constraint_predicates(inst)
    m = len(preds)
    n = inst.n_problem_qubits
    trace, tokens = [], dict(tokens_in=0, tokens_out=0, cost_usd=0.0)
    # the unit bench offers exactly the scratch the ASSEMBLY can afford
    # (best plan), so over-consuming fragments fail early with actionable
    # feedback instead of crashing at assembly time
    avail = inst.max_total_qubits - n
    plan_a_scratch = avail - m
    plan_c_scratch = avail - 1 - counter_width(m)
    plan_c2_scratch = (avail - 1 - counter_width(m - 1)) if m > 1 else 0
    bench_scratch_n = max(plan_a_scratch, plan_c_scratch,
                          plan_c2_scratch, 0)
    clist = "\n".join(f"{j + 1}. {name}" for j, (name, _) in enumerate(preds))
    clist += (f"\n\nBudget note: `scratch` has EXACTLY {bench_scratch_n} "
              "qubits; use as few as possible (0 where doable).")
    if opt["self_assembly"]:
        clist += SELF_ASSEMBLY_NOTE
    prompt = UNIT_PROMPT.format(problem=inst.problem_text,
                                constraints=clist)
    # bench layout deliberately differs from deployment (flag on the LAST
    # wire, scratch first) so fragments hardcoding literal indices instead
    # of using the passed arguments fail their unit checks
    total_bench = min(20, n + 1 + bench_scratch_n)
    flag_bench = total_bench - 1
    scratch_bench = list(range(n, total_bench - 1))

    src_parts: dict[int, str] = {}
    text = ""
    max_scratch_used = 0
    for rnd in range(opt["max_fragment_rounds"] + 1):
        reply = client.complete(prompt, temperature)
        text = reply.text
        for k in tokens:
            tokens[k] += getattr(reply, k)
        src = _extract_fragments(reply.text)
        if src is None:
            trace.append({"stage": "fragments", "round": rnd,
                          "result": "no_fragments_extracted"})
            prompt += "\nYour reply contained no build_constraint_j code."
            continue
        # merge newly provided fragments over previous ones
        ns: dict = {}
        try:
            exec(compile(src, "<frags>", "exec"), ns)
        except Exception as e:
            trace.append({"stage": "fragments", "round": rnd,
                          "result": f"exec_error: {e}"})
            prompt += f"\nYour code failed to run: {e}"
            continue
        for j in range(m):
            if f"build_constraint_{j + 1}" in ns:
                src_parts[j] = src
        reports = []
        for j, (name, pred) in enumerate(preds):
            if j not in src_parts:
                reports.append(f"- constraint {j + 1} ({name}): function "
                               "missing")
                continue
            # policy: the banned-API rules apply inside fragments too
            # (the L1 scan cannot see into the embedded source string)
            import ast as _ast
            from qencodebench.verifier.verify import _banned_api
            banned = _banned_api(_ast.parse(src_parts[j]))
            if banned is not None:
                reports.append(f"- constraint {j + 1} ({name}): uses "
                               f"banned API '{banned}'")
                continue
            ns_j: dict = {}
            exec(compile(src_parts[j], "<frag>", "exec"), ns_j)
            ok, report, used = unit_verify(
                ns_j[f"build_constraint_{j + 1}"], pred, n, total_bench,
                flag_bench, scratch_bench)
            if ok:
                max_scratch_used = max(
                    max_scratch_used,
                    max((scratch_bench.index(w) + 1 for w in used),
                        default=0))
            elif opt["feedback_granularity"] == "which_only":
                reports.append(f"- constraint {j + 1} ({name}): FAILED "
                               "its unit check")
            else:
                reports.append(f"- constraint {j + 1} ({name}):\n{report}")
        trace.append({"stage": "fragments", "round": rnd,
                      "failing": len(reports)})
        if not reports:
            break
        prompt = (UNIT_PROMPT.format(problem=inst.problem_text,
                                     constraints=clist)
                  + FRAGMENT_FEEDBACK.format(reports="\n".join(reports)))
    else:
        trace.append({"stage": "fragments", "result": "rounds_exhausted"})

    code = None
    if opt["self_assembly"]:
        from qencodebench.pipeline.extract import extract_code
        code = extract_code(text)          # the model's own build_oracle
    elif len(src_parts) == m:
        per_fragment = {str(j): src_parts[j] for j in range(m)}
        code = emit_build_oracle_code(per_fragment, m, agg,
                                      max_scratch_used)
    return {
        "response_text": text,
        "extracted_code": code,
        "agent_trace": trace,
        "agent_budget_exceeded": False,
        **tokens,
    }
