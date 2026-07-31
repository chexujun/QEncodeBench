"""F7: mixed-structure family (frozen_v1.1).

f(x) = (all 3-SAT clauses satisfied)  AND  (popcount(x) cmp k),
cmp in {==, <=, >=}.  A single instance requires BOTH encoding techniques
(clause logic + cardinality counter) -- probing the "knows each trick but
cannot combine them" gap.

Encoding domain == problem domain.  Qubit account: n vars + m clause
flags + weight counter ceil(log2(n+1)); budget n + m + w <= 20.
"""

from __future__ import annotations

import random

from qiskit import QuantumCircuit

from qencodebench.core.task import (
    TaskInstance, TaskGenerator, GeneratorReject, stable_rng_seed,
    GLOBAL_QUBIT_CAP, tier_label,
)
from qencodebench.core.circuits import (
    flag_on_pattern, phase_on_pattern, counter_width,
    controlled_increment, controlled_decrement,
)
from qencodebench.generators.f1_sat import SatGenerator, clause_satisfied

MAX_TRIES = 800

TIER_PARAMS = {
    1: dict(n_choices=[6, 7], m_range=(3, 4)),
    2: dict(n_choices=[7, 8], m_range=(4, 5)),
    3: dict(n_choices=[8, 9], m_range=(5, 6)),
}

_CMP = {"==": lambda a, b: a == b, "<=": lambda a, b: a <= b,
        ">=": lambda a, b: a >= b}


class SatCardGenerator(TaskGenerator):
    family = "sat_card"
    tiers = (1, 2, 3)

    def generate(self, tier: int, seed: int) -> TaskInstance:
        params = TIER_PARAMS[tier]
        for sub in range(MAX_TRIES):
            rng = random.Random(stable_rng_seed(self.family, tier, seed, sub))
            n = rng.choice(params["n_choices"])
            lo, hi = params["m_range"]
            m = rng.randint(lo, hi)
            clauses = SatGenerator._draw_clauses(rng, n, m)
            if clauses is None:
                self._record_reject(tier, seed, sub, "duplicate_clauses")
                continue
            cmp_ = rng.choice(["==", "<=", ">="])
            k = rng.randint(2, n - 2)
            w = counter_width(n)
            budget = n + m + w
            if budget > GLOBAL_QUBIT_CAP:
                self._record_reject(tier, seed, sub, f"budget:{budget}")
                continue
            spec = {"n_vars": n, "clauses": clauses, "cmp": cmp_, "k": k}
            inst = TaskInstance(
                task_id=f"sat_card-{tier_label(tier)}-s{seed:04d}",
                family=self.family, tier=tier, seed=seed,
                problem_text="", formal_spec=spec,
                n_problem_qubits=n,
                max_total_qubits=budget,
                max_depth=0,
            )
            try:
                self._check_instance(inst, self.classical_solutions(inst))
            except GeneratorReject as ex:
                self._record_reject(tier, seed, sub, ex.reason)
                continue
            inst.problem_text = render_verbose(spec)
            return self.finalize(inst)
        raise RuntimeError(f"sat_card T{tier} s{seed}: retries exhausted")

    def classical_solutions(self, inst: TaskInstance) -> set[int]:
        spec = inst.formal_spec
        n, clauses = spec["n_vars"], spec["clauses"]
        cmp_fn, k = _CMP[spec["cmp"]], spec["k"]
        return {
            x for x in range(1 << n)
            if all(clause_satisfied(c, x) for c in clauses)
            and cmp_fn(bin(x).count("1"), k)
        }

    def reference_oracle(self, inst: TaskInstance) -> QuantumCircuit:
        spec = inst.formal_spec
        n, clauses = spec["n_vars"], spec["clauses"]
        cmp_fn, k = _CMP[spec["cmp"]], spec["k"]
        m = len(clauses)
        w = counter_width(n)
        qc = QuantumCircuit(n + m + w)
        flags = list(range(n, n + m))
        counter = list(range(n + m, n + m + w))

        def compute_flags():
            for j, clause in enumerate(clauses):
                variables = [v for v, _ in clause]
                flag_on_pattern(qc, variables,
                                [1 - pos for _, pos in clause], flags[j])
                qc.x(flags[j])

        compute_flags()
        for i in range(n):
            controlled_increment(qc, [i], counter)
        for t in range(n + 1):
            if cmp_fn(t, k):
                phase_on_pattern(qc, flags + counter,
                                 [1] * m + [(t >> i) & 1 for i in range(w)])
        for i in range(n):
            controlled_decrement(qc, [i], counter)
        compute_flags()
        return qc


# ---- problem-text rendering -------------------------------------------------

def _fmt_clause(clause) -> str:
    return "(" + " OR ".join(
        (f"x{v}" if pos else f"NOT x{v}") for v, pos in clause) + ")"


_CMP_TEXT = {"==": "EXACTLY", "<=": "AT MOST", ">=": "AT LEAST"}


def render_verbose(spec: dict) -> str:
    n, clauses = spec["n_vars"], spec["clauses"]
    lines = [
        f"We have {n} Boolean variables x0..x{n-1} (variable x_i on "
        "problem_qubits[i], basis value 1 = True) subject to TWO KINDS of "
        "constraints simultaneously:",
        "",
        "A. a 3-SAT formula (every clause must hold):",
    ]
    lines += ["  " + _fmt_clause(c) for c in clauses]
    lines += [
        "",
        f"B. a cardinality constraint: the number of variables set to "
        f"True must be {_CMP_TEXT[spec['cmp']]} {spec['k']}.",
        "",
        "The classical predicate is f(x) = 1 if and only if BOTH the "
        "formula (A) and the cardinality condition (B) hold.",
    ]
    return "\n".join(lines)


def render_terse(spec: dict) -> str:
    cl = " AND ".join(_fmt_clause(c) for c in spec["clauses"])
    return (f"Mixed constraints, n={spec['n_vars']} vars (x_i on "
            f"problem_qubits[i]). f(x)=1 iff [{cl}] AND "
            f"popcount(x) {spec['cmp']} {spec['k']}.")
