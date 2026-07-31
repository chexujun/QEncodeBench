"""14 mutant oracles for verifier self-checking.

12 logic-defect mutants + 2 basis-permutation mutants.  Every mutant must be
REJECTED by L3.  The two permutation mutants (13, 14) are constructed to be
invisible on the uniform superposition (step 1 + step 3 both look correct),
so only the random-fingerprint diagonality check (step 2) can catch them --
they are the permanent regression tests for that step.

Each mutant factory returns (name, circuit, inst, solutions).  The mutant is
built so that its marked set provably differs from the true solution set
(asserted at construction time).
"""

from __future__ import annotations

import numpy as np
from qiskit import QuantumCircuit

from qencodebench.core.circuits import (
    flag_on_pattern, phase_on_pattern, flag_colors_differ,
    controlled_increment, controlled_decrement, controlled_add_const,
    controlled_sub_const, counter_width,
)
from qencodebench.generators import get_generator
from qencodebench.generators.f1_sat import clause_satisfied


def _sat_fixture():
    gen = get_generator("3sat")
    inst = gen.generate(2, 42)
    sols = gen.classical_solutions(inst)
    ref = gen.reference_oracle(inst)
    return gen, inst, sols, ref


def _sat_oracle_custom(n: int, clauses, *, skip_uncompute=False,
                       skip_phase=False, double_phase=False,
                       and_semantics=False,
                       phase_pattern_flip: int | None = None) -> QuantumCircuit:
    """SAT reference oracle with injectable defects."""
    m = len(clauses)
    qc = QuantumCircuit(n + m)
    flags = list(range(n, n + m))

    def compute():
        for j, clause in enumerate(clauses):
            variables = [v for v, _ in clause]
            if and_semantics:
                # DEFECT: flag = all literals true (AND instead of OR)
                flag_on_pattern(qc, variables, [p for _, p in clause],
                                flags[j])
            else:
                flag_on_pattern(qc, variables, [1 - p for _, p in clause],
                                flags[j])
                qc.x(flags[j])

    compute()
    if not skip_phase:
        pattern = [1] * m
        if phase_pattern_flip is not None:
            pattern[phase_pattern_flip] = 0
        phase_on_pattern(qc, flags, pattern)
        if double_phase:
            phase_on_pattern(qc, flags, pattern)
    if not skip_uncompute:
        compute()
    return qc


def _sat_solutions(n: int, clauses) -> set[int]:
    return {x for x in range(1 << n)
            if all(clause_satisfied(c, x) for c in clauses)}


def _pick_modified_clauses(inst, sols, modify) -> list:
    """Apply ``modify`` to each clause index until the solution set changes."""
    n = inst.formal_spec["n_vars"]
    clauses = inst.formal_spec["clauses"]
    for j in range(len(clauses)):
        mod = modify(clauses, j)
        if mod is not None and _sat_solutions(n, mod) != sols:
            return mod
    raise AssertionError("no modification changed the solution set")


def build_mutants() -> list[tuple[str, QuantumCircuit, object, set[int]]]:
    out = []
    gen, inst, sols, ref = _sat_fixture()
    n = inst.formal_spec["n_vars"]
    clauses = inst.formal_spec["clauses"]

    # 1. dropped constraint: oracle built from m-1 clauses
    mod = _pick_modified_clauses(
        inst, sols, lambda cs, j: cs[:j] + cs[j + 1:])
    out.append(("M01_drop_constraint",
                _sat_oracle_custom(n, mod), inst, sols))

    # 2. phase direction flipped for half the basis states (extra Z)
    qc = ref.copy()
    qc.z(0)
    out.append(("M02_partial_phase_flip", qc, inst, sols))

    # 3. ancilla not uncomputed
    out.append(("M03_dirty_ancilla",
                _sat_oracle_custom(n, clauses, skip_uncompute=True),
                inst, sols))

    # 4. literal polarity flipped in one clause (wrong X-conjugation)
    def flip_pol(cs, j):
        mod = [list(map(list, c)) for c in cs]
        mod[j][0][1] ^= 1
        return mod
    out.append(("M04_wrong_polarity",
                _sat_oracle_custom(n, _pick_modified_clauses(inst, sols,
                                                             flip_pol)),
                inst, sols))

    # 5. off-by-one qubit index in one clause
    def shift_var(cs, j):
        mod = [list(map(list, c)) for c in cs]
        v = (mod[j][0][0] + 1) % n
        if v in [w for w, _ in mod[j]]:
            return None
        mod[j][0][0] = v
        return mod
    out.append(("M05_off_by_one_qubit",
                _sat_oracle_custom(n, _pick_modified_clauses(inst, sols,
                                                             shift_var)),
                inst, sols))

    # 6. forgotten phase gate (identity marking)
    out.append(("M06_missing_phase",
                _sat_oracle_custom(n, clauses, skip_phase=True), inst, sols))

    # 7. OR of literals implemented as AND
    out.append(("M07_and_instead_of_or",
                _sat_oracle_custom(n, clauses, and_semantics=True),
                inst, sols))

    # 8. wrong control polarity on the final multi-controlled phase
    out.append(("M08_phase_pattern_error",
                _sat_oracle_custom(n, clauses, phase_pattern_flip=0),
                inst, sols))

    # 9. phase applied twice (cancels out)
    out.append(("M09_double_phase",
                _sat_oracle_custom(n, clauses, double_phase=True),
                inst, sols))

    # 10. F2: non-surjective comparator (treats 11 as a 4th color)
    cgen = get_generator("coloring")
    cinst = cgen.generate(1, 42)
    csols = cgen.classical_solutions(cinst)
    out.append(("M10_nonsurjective_comparator",
                _coloring_naive_oracle(cinst), cinst, csols))

    # 11. F4: comparator against T+1
    sgen = get_generator("subset_sum")
    sinst = sgen.generate(1, 42)
    ssols = sgen.classical_solutions(sinst)
    out.append(("M11_wrong_target",
                _subset_sum_oracle(sinst, target_shift=1), sinst, ssols))

    # 12. F3: size bound k+1 instead of k
    vgen = get_generator("vertex_cover")
    vinst, vsols = None, None
    for seed in range(1, 60):
        cand = vgen.generate(1, seed)
        csol = vgen.classical_solutions(cand)
        loose = _vc_solutions(cand, k_shift=1)
        if loose != csol:
            vinst, vsols = cand, csol
            break
    assert vinst is not None, "no vertex_cover instance where k+1 differs"
    out.append(("M12_wrong_k_bound",
                _vertex_cover_oracle(vinst, k_shift=1), vinst, vsols))

    # 13. basis swap of two same-f states (fools the uniform screen)
    a, b, t = _find_swap_pair(n, sols)
    qc = ref.copy()
    controls = [q for q in range(n) if q != t]
    flag_on_pattern(qc, controls, [(a >> q) & 1 for q in controls], t)
    out.append(("M13_basis_swap", qc, inst, sols))

    # 14. phased 3-cycle, phases tuned to cancel on the uniform state
    out.append(("M14_phased_3cycle",
                _phased_3cycle_mutant(ref, n, sols), inst, sols))

    # 15. rolling-counter window offset (frozen_v1.1 T3p regression):
    #     phase fires on count == m-1 instead of m
    rgen = get_generator("3sat")
    rinst = rgen.generate(4, 7)
    rsols = rgen.classical_solutions(rinst)
    out.append(("M15_rolling_window_offset",
                _sat_rolling_offset_oracle(rinst), rinst, rsols))

    # 16. F7 cross-contamination: the cardinality patterns are applied to
    #     the CLAUSE counter instead of the weight counter
    xgen = get_generator("sat_card")
    xinst = xgen.generate(2, 7)
    xsols = xgen.classical_solutions(xinst)
    out.append(("M16_satcard_counter_mixup",
                _satcard_mixup_oracle(xinst), xinst, xsols))

    assert len(out) == 16
    return out


def _sat_rolling_offset_oracle(inst) -> QuantumCircuit:
    """F1 rolling reference with the phase window off by one (m-1)."""
    from qencodebench.core.circuits import (
        controlled_increment as inc, controlled_decrement as dec,
    )
    n = inst.formal_spec["n_vars"]
    clauses = inst.formal_spec["clauses"]
    m = len(clauses)
    w = counter_width(m)
    qc = QuantumCircuit(n + 1 + w)
    flag, counter = n, list(range(n + 1, n + 1 + w))

    def clause_flag(j):
        variables = [v for v, _ in clauses[j]]
        flag_on_pattern(qc, variables,
                        [1 - pos for _, pos in clauses[j]], flag)
        qc.x(flag)

    for j in range(m):
        clause_flag(j); inc(qc, [flag], counter); clause_flag(j)
    wrong = m - 1                       # DEFECT: off-by-one window
    phase_on_pattern(qc, counter, [(wrong >> i) & 1 for i in range(w)])
    for j in reversed(range(m)):
        clause_flag(j); dec(qc, [flag], counter); clause_flag(j)
    return qc


def _satcard_mixup_oracle(inst) -> QuantumCircuit:
    """F7 reference with the cardinality check applied to the CLAUSE
    counter (structure mix-up between the two techniques)."""
    spec = inst.formal_spec
    n, clauses, k = spec["n_vars"], spec["clauses"], spec["k"]
    cmp_fn = {"==": lambda a, b: a == b, "<=": lambda a, b: a <= b,
              ">=": lambda a, b: a >= b}[spec["cmp"]]
    m = len(clauses)
    w = counter_width(m)
    qc = QuantumCircuit(n + w)
    counter = list(range(n, n + w))
    # count SATISFIED CLAUSES (not popcount!) then apply the k-condition
    for j, clause in enumerate(clauses):
        variables = [v for v, _ in clause]
        # roll each clause into the counter via a phase-free trick:
        # increment controlled on "clause satisfied" needs a flag; borrow
        # counter-free structure: increment on each TRUE literal pattern
        # is wrong anyway -- keep it simple: increment when first literal
        # true (a plausible-looking but doubly wrong construction)
        v0, pos0 = clause[0]
        from qencodebench.core.circuits import controlled_increment as inc
        if pos0:
            inc(qc, [v0], counter)
        else:
            qc.x(v0); inc(qc, [v0], counter); qc.x(v0)
    for t in range(m + 1):
        if cmp_fn(t, k):
            phase_on_pattern(qc, counter,
                             [(t >> i) & 1 for i in range(w)])
    for j, clause in enumerate(reversed(clauses)):
        v0, pos0 = clause[0]
        from qencodebench.core.circuits import controlled_decrement as dec
        if pos0:
            dec(qc, [v0], counter)
        else:
            qc.x(v0); dec(qc, [v0], counter); qc.x(v0)
    return qc


# ---- helper oracle builders -------------------------------------------------

def _coloring_naive_oracle(inst) -> QuantumCircuit:
    """DEFECT: colors 'differ' iff codes differ bitwise (11 != 00)."""
    v = inst.formal_spec["n_vertices"]
    edges = inst.formal_spec["edges"]
    e = len(edges)
    qc = QuantumCircuit(2 * v + e)
    flags = list(range(2 * v, 2 * v + e))

    def compute():
        for j, (a, b) in enumerate(edges):
            qc.cx(2 * a, 2 * b)
            qc.cx(2 * a + 1, 2 * b + 1)
            flag_on_pattern(qc, [2 * b, 2 * b + 1], [0, 0], flags[j])
            qc.cx(2 * a + 1, 2 * b + 1)
            qc.cx(2 * a, 2 * b)
            qc.x(flags[j])

    compute()
    phase_on_pattern(qc, flags, [1] * e)
    compute()
    return qc


def _subset_sum_oracle(inst, target_shift: int) -> QuantumCircuit:
    values = inst.formal_spec["values"]
    target = inst.formal_spec["target"] + target_shift
    e = len(values)
    w = counter_width(sum(values))
    qc = QuantumCircuit(e + w)
    reg = list(range(e, e + w))
    for i, a in enumerate(values):
        controlled_add_const(qc, [i], reg, a)
    phase_on_pattern(qc, reg, [(target >> i) & 1 for i in range(w)])
    for i, a in enumerate(values):
        controlled_sub_const(qc, [i], reg, a)
    return qc


def _vc_solutions(inst, k_shift: int) -> set[int]:
    n = inst.formal_spec["n_vertices"]
    edges = inst.formal_spec["edges"]
    k = inst.formal_spec["k"] + k_shift
    return {x for x in range(1 << n)
            if bin(x).count("1") <= k
            and all((x >> a) & 1 or (x >> b) & 1 for a, b in edges)}


def _vertex_cover_oracle(inst, k_shift: int) -> QuantumCircuit:
    n = inst.formal_spec["n_vertices"]
    edges = inst.formal_spec["edges"]
    k = inst.formal_spec["k"] + k_shift
    e = len(edges)
    w = counter_width(n)
    qc = QuantumCircuit(n + e + w)
    flags = list(range(n, n + e))
    counter = list(range(n + e, n + e + w))

    def compute():
        for j, (a, b) in enumerate(edges):
            qc.x(flags[j])
            flag_on_pattern(qc, [a, b], [0, 0], flags[j])

    compute()
    for i in range(n):
        controlled_increment(qc, [i], counter)
    for t in range(k + 1):
        phase_on_pattern(qc, flags + counter,
                         [1] * e + [(t >> i) & 1 for i in range(w)])
    for i in range(n):
        controlled_decrement(qc, [i], counter)
    compute()
    return qc


def _find_swap_pair(n: int, sols: set[int]) -> tuple[int, int, int]:
    """Two basis states differing in exactly one bit with equal f."""
    for a in range(1 << n):
        for t in range(n):
            b = a ^ (1 << t)
            if a < b and ((a in sols) == (b in sols)):
                return a, b, t
    raise AssertionError("no same-f neighbouring pair")


def _phased_3cycle_mutant(ref: QuantumCircuit, n: int,
                          sols: set[int]) -> QuantumCircuit:
    """Compose the correct oracle with a 3-cycle a->b->c->a whose leg phases
    (-1)^(f(dst) xor f(src)) make the uniform superposition come out exactly
    right -- only the fingerprint magnitude check can catch it."""
    dim = 1 << n
    inside = sorted(sols)
    outside = [x for x in range(dim) if x not in sols]
    # mixed f values so the leg phases are non-trivial
    a, b, c = inside[0], outside[0], inside[-1]
    assert len({a, b, c}) == 3
    f = lambda x: 1 if x in sols else 0        # noqa: E731

    mat = np.eye(dim, dtype=complex)
    for src, dst in ((a, b), (b, c), (c, a)):
        mat[:, src] = 0
        mat[dst, src] = (-1) ** (f(dst) ^ f(src))
    qc = ref.copy()
    qc.unitary(mat, list(range(n)), label="cycle3")
    return qc
