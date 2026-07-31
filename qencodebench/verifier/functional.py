"""L3 functional verification.

Correctness is defined modulo a global phase: U is correct iff there exists
theta such that U|x>|0>_anc = e^(i*theta) * (-1)^f(x) |x>|0>_anc for every
basis state x.  In particular "mark the non-solutions" differs from "mark the
solutions" only by a global -1 and MUST pass.

Method A (default, 3 simulations):
  step 1: uniform-superposition phase readout (1 sim),
  step 2: two random-fingerprint diagonality checks (2 sims),
  step 3: compare the relative phase table with pi*(f(x) xor f(0)).

Exhaustive check (2^n sims) is used (a) as escalation when a fast-path PASS
is within the edge margins, (b) on a random 5% of passing samples,
(c) for diagnosis of failing samples when n_problem <= EXHAUSTIVE_DIAG_MAX.

Method B (Operator equivalence, <= 10 total qubits) is available for
cross-checking in the self-check suite.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from qiskit import QuantumCircuit

from qencodebench.core.sim import run_statevector

TOL_PHASE = 1e-6
TOL_MAG = 1e-6
TOL_LEAK = 1e-9
# Edge margins: fast-path PASSes not clearing these are re-checked exhaustively
EDGE_PHASE = TOL_PHASE / 10
# NOTE: the uniform/fingerprint leak is an AGGREGATE over 2^n states while
# the exhaustive ground truth bounds leak PER STATE (TOL_LEAK).  A single
# state leaking epsilon appears as ~epsilon/2^n in the aggregate, so the
# escalation threshold must scale with the dimension (see method_a);
# numerical noise sits ~1e-24 in aggregate weight, far below.
EDGE_LEAK = 1e-10
EDGE_MAG = TOL_MAG / 10
RANDOM_EXHAUSTIVE_FRACTION = 0.05
EXHAUSTIVE_DIAG_MAX = 10        # max n_problem for exhaustive failure diagnosis
# Pathological candidate circuits (loop bugs emitting 100k+ gates) make the
# 2^n-simulation exhaustive path take hours; above this gate count the
# diagnosis falls back to the phase table (PASS/FAIL semantics unaffected).
MAX_DIAG_CIRCUIT_SIZE = 30_000
MAX_COUNTEREXAMPLES = 8


@dataclass
class FuncResult:
    passed: bool
    fail_reason: str | None = None      # ANCILLA_DIRTY | BASIS_CORRUPTION |
                                        # MARK_MISMATCH | None
    mark_accuracy: float | None = None
    counterexamples: list[int] = field(default_factory=list)
    method: str = "A"                   # A | A+exhaustive | exhaustive
    max_phase_dev: float = 0.0
    max_leak: float = 0.0
    # transient: observed marked set (phase ~ pi states) on MARK_MISMATCH,
    # feeds constraint-level behavioral diagnosis; not serialized to rows
    marked: list[int] | None = None


def _phase_dist(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Pointwise distance between phases, mod 2*pi, in [0, pi]."""
    d = np.abs(np.angle(np.exp(1j * (a - b))))
    return d


def _f_vector(n: int, solutions: set[int]) -> np.ndarray:
    f = np.zeros(1 << n, dtype=np.int8)
    for s in solutions:
        f[s] = 1
    return f


def _accuracy_and_counterexamples(cls_rel: np.ndarray, valid: np.ndarray,
                                  f: np.ndarray):
    """Best accuracy over the two global-flip hypotheses + stratified
    counterexamples (up to 4 missed marks + 4 false marks)."""
    accs = []
    for g in (0, 1):
        pred = np.where(valid, cls_rel ^ g, -1)
        accs.append(float(np.mean(pred == f)))
    g_best = int(np.argmax(accs))
    pred = np.where(valid, cls_rel ^ g_best, -1)
    wrong = np.nonzero(pred != f)[0]
    missed = [int(x) for x in wrong if f[x] == 1]
    false = [int(x) for x in wrong if f[x] == 0]
    half = MAX_COUNTEREXAMPLES // 2
    take_m = missed[:half]
    take_f = false[:half]
    # top up from the other stratum if one side is short
    take_m += missed[half:half + (half - len(take_f))]
    take_f += false[half:half + (half - len(take_m))]
    return max(accs), (take_m + take_f)[:MAX_COUNTEREXAMPLES]


def _classify_phases(rel_phase: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Map relative phases to bits {0,1}; valid=False if neither 0 nor pi."""
    d0 = _phase_dist(rel_phase, np.zeros_like(rel_phase))
    d1 = _phase_dist(rel_phase, np.full_like(rel_phase, np.pi))
    cls = (d1 < d0).astype(np.int8)
    valid = np.minimum(d0, d1) <= TOL_PHASE
    return cls, valid


def _fingerprint_state(rng: np.random.Generator, n: int,
                       total: int) -> np.ndarray:
    dim = 1 << n
    mags = rng.uniform(0.5, 1.5, size=dim)
    phases = rng.uniform(0, 2 * np.pi, size=dim)
    c = mags * np.exp(1j * phases)
    c /= np.linalg.norm(c)
    full = np.zeros(1 << total, dtype=complex)
    full[:dim] = c
    return full


def method_a(oracle: QuantumCircuit, n_problem: int,
             solutions: set[int]) -> FuncResult:
    n = n_problem
    total = oracle.num_qubits
    dim = 1 << n
    f = _f_vector(n, solutions)

    # ---- step 1: uniform-superposition phase readout ---------------------
    prep = QuantumCircuit(total)
    prep.h(range(n))
    prep.compose(oracle, inplace=True)
    sv = run_statevector(prep)
    block = sv[:dim]
    leak = float(1.0 - np.sum(np.abs(block) ** 2))
    if leak > TOL_LEAK:
        return _diagnose_fail(oracle, n, f, "ANCILLA_DIRTY", leak=leak)
    expected_mag = 2 ** (-n / 2)
    mag_dev = float(np.max(np.abs(np.abs(block) - expected_mag)))
    if mag_dev > TOL_MAG:
        return _diagnose_fail(oracle, n, f, "BASIS_CORRUPTION", leak=leak)
    base = block[0]
    # guard against a vanishing reference component
    assert abs(base) > 0.5 * expected_mag, "reference amplitude too small"
    rel = np.angle(block / base)

    # ---- step 3 (cheap, do before fingerprints for early fail diagnosis) --
    target = np.pi * (f ^ f[0]).astype(float)
    dev = _phase_dist(rel, target)
    max_dev = float(np.max(dev))
    if max_dev > TOL_PHASE:
        return _diagnose_fail(oracle, n, f, "MARK_MISMATCH",
                              rel_phase=rel, leak=leak, max_dev=max_dev)

    # ---- step 2: two random-fingerprint diagonality checks ----------------
    rng = np.random.default_rng(0xF1A6E5)   # fixed, recorded fingerprints
    max_fp_dev = 0.0
    for _ in range(2):
        c = _fingerprint_state(rng, n, total)
        out = run_statevector(oracle, initial=c)
        fp_leak = float(1.0 - np.sum(np.abs(out[:dim]) ** 2))
        if fp_leak > TOL_LEAK:
            return _diagnose_fail(oracle, n, f, "ANCILLA_DIRTY", leak=fp_leak)
        fp_dev = float(np.max(np.abs(np.abs(out[:dim]) - np.abs(c[:dim]))))
        max_fp_dev = max(max_fp_dev, fp_dev)
        if fp_dev > TOL_MAG:
            return _diagnose_fail(oracle, n, f, "BASIS_CORRUPTION",
                                  leak=fp_leak)
        # cross-check fingerprint relative phases against step 1
        rel_fp = np.angle(out[:dim] / c[:dim])
        rel_fp = rel_fp - rel_fp[0]
        if float(np.max(_phase_dist(rel_fp, rel))) > TOL_PHASE:
            return _diagnose_fail(oracle, n, f, "MARK_MISMATCH",
                                  rel_phase=rel, leak=leak, max_dev=max_dev)
        leak = max(leak, fp_leak)

    result = FuncResult(passed=True, mark_accuracy=1.0, method="A",
                        max_phase_dev=max_dev, max_leak=leak)
    # ---- edge-condition escalation --------------------------
    # leak threshold scales with dimension: aggregate epsilon/dim can hide
    # a per-state epsilon > TOL_LEAK that the exhaustive standard rejects
    leak_edge = min(EDGE_LEAK, TOL_LEAK / (10 * dim))
    if max_dev > EDGE_PHASE or leak > leak_edge or max_fp_dev > EDGE_MAG:
        # the exhaustive standard is AUTHORITATIVE for edge cases: its
        # verdict (either way) replaces the fast-path one
        if dim * max(oracle.size(), 1) <= 5e8:      # in-process cost gate
            ex = exhaustive(oracle, n, solutions)
            ex.method = "A+exhaustive"
            return ex
        result.method = "A(edge-escalation-skipped:cost)"
    return result


def _diagnose_fail(oracle, n, f, reason, rel_phase=None, leak=0.0,
                   max_dev=0.0) -> FuncResult:
    """On failure, produce mark_accuracy + stratified counterexamples.

    Uses exhaustive per-basis-state diagnosis when affordable, else falls
    back to the phase table (when available)."""
    if n <= EXHAUSTIVE_DIAG_MAX and oracle.size() <= MAX_DIAG_CIRCUIT_SIZE:
        ex = exhaustive(oracle, n, set(np.nonzero(f)[0].tolist()))
        ex.method = "A+exhaustive"
        if ex.passed:
            # the per-basis-state exhaustive standard is authoritative:
            # method A's aggregate screens can trip on deviations that are
            # within per-state tolerance (e.g. leak spread over 2^n).
            # Keep the pass, but tag it for the run log.
            ex.method = "exhaustive-overrides-A(" + reason + ")"
        else:
            ex.fail_reason = ex.fail_reason or reason
        return ex
    if rel_phase is not None:
        cls, valid = _classify_phases(rel_phase)
        acc, ces = _accuracy_and_counterexamples(cls, valid, f)
        marked = [int(x) for x in np.nonzero(cls == 1)[0]]
        return FuncResult(False, reason, acc, ces, "A", max_dev, leak,
                          marked=marked)
    return FuncResult(False, reason, None, [], "A", max_dev, leak)


def exhaustive(oracle: QuantumCircuit, n_problem: int,
               solutions: set[int]) -> FuncResult:
    """Basis-state-by-basis-state check: 2^n simulations."""
    n = n_problem
    total = oracle.num_qubits
    dim = 1 << n
    f = _f_vector(n, solutions)
    comp = np.zeros(dim, dtype=complex)
    per_x_ok = np.ones(dim, dtype=bool)
    max_leak = 0.0
    for x in range(dim):
        init = np.zeros(1 << total, dtype=complex)
        init[x] = 1.0
        out = run_statevector(oracle, initial=init)
        comp[x] = out[x]
        leak_x = float(1.0 - abs(out[x]) ** 2)
        max_leak = max(max_leak, leak_x)
        if leak_x > TOL_LEAK:
            per_x_ok[x] = False
    base = comp[0] if abs(comp[0]) > 1e-12 else 1.0
    rel = np.angle(comp / base)
    cls, phase_valid = _classify_phases(rel)
    valid = per_x_ok & phase_valid
    target = (f ^ f[0]).astype(np.int8)
    correct = valid & (cls == target)
    passed = bool(np.all(correct))
    acc, ces = _accuracy_and_counterexamples(cls, valid, f)
    if passed:
        return FuncResult(True, None, 1.0, [], "exhaustive",
                          float(np.max(_phase_dist(
                              rel, np.pi * target.astype(float)))), max_leak)
    reason = "MARK_MISMATCH"
    if np.any(~per_x_ok):
        # distinguish dirty ancilla from basis corruption on the worst state
        x_bad = int(np.nonzero(~per_x_ok)[0][0])
        init = np.zeros(1 << total, dtype=complex)
        init[x_bad] = 1.0
        out = run_statevector(oracle, initial=init)
        anc_leak = float(np.sum(np.abs(out[dim:]) ** 2))
        reason = "ANCILLA_DIRTY" if anc_leak > TOL_LEAK else "BASIS_CORRUPTION"
    marked = ([int(x) for x in np.nonzero(cls == 1)[0]]
              if reason == "MARK_MISMATCH" else None)
    return FuncResult(False, reason, acc, ces, "exhaustive", 0.0, max_leak,
                      marked=marked)


def method_b(oracle: QuantumCircuit, n_problem: int,
             solutions: set[int]) -> bool:
    """Unitary-equivalence cross-check (total qubits <= 10)."""
    from qiskit.quantum_info import Operator

    n = n_problem
    total = oracle.num_qubits
    if total > 10:
        raise ValueError("method B limited to 10 total qubits")
    dim = 1 << n
    f = _f_vector(n, solutions)
    u = Operator(oracle).data
    theta = None
    for x in range(dim):
        col = u[:, x]
        ex = np.zeros(1 << total, dtype=complex)
        ex[x] = 1.0
        amp = col[x]
        if abs(abs(amp) - 1.0) > TOL_MAG:
            return False
        if float(np.linalg.norm(col - amp * ex)) > TOL_MAG:
            return False
        ph = np.angle(amp) - np.pi * float(f[x])
        if theta is None:
            theta = ph
        elif float(np.abs(np.angle(np.exp(1j * (ph - theta))))) > TOL_PHASE:
            return False
    return True
