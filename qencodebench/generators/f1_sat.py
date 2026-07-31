"""F1: 3-SAT -> Grover phase oracle.

Encoding domain == problem domain (bitstring is the assignment), so the
surjective-code family rule does not apply here.

Qubit account: n variables + m clause flags + 1 kickback slack.
Budget formula: n + m + 1, with m <= 19 - n so the budget stays <= 20.
The reference oracle itself uses n + m qubits (MCZ across clause flags).
"""

from __future__ import annotations

import random

from qiskit import QuantumCircuit

from qencodebench.core.task import (
    TaskInstance, TaskGenerator, GeneratorReject, stable_rng_seed,
    tier_label,
)
from qencodebench.core.circuits import (
    flag_on_pattern, phase_on_pattern, counter_width,
    controlled_increment, controlled_decrement,
)

MAX_TRIES = 500

# T1 uses m=4..5 instead of the design's m=2 example: a 3-clause-or-fewer
# formula over 3+ vars excludes at most 3 * 2^(n-3) < 2^(n-1) assignments,
# so the solution-density filter (<= 1/2) can never pass.  Yield-rule
# adjustment applied.
# Tier 4 (T3p): zero-slack rolling budget n + 1 + ceil(log2(m+1)) forces
# ancilla reuse.  Tier 5 (T4): scale-up to the n <= 12 verifier red line.
TIER_PARAMS = {
    1: dict(n_choices=[3, 4], m_range=(4, 5)),
    2: dict(n_choices=[4, 5, 6], m_range=(3, 6)),
    3: dict(n_choices=[6, 7, 8], m_range=(7, None)),   # None -> 19 - n
    4: dict(n_choices=[5, 6], m_range=(7, 10), rolling=True),
    5: dict(n_choices=[10, 11, 12], m_range=(6, None)),
}


def clause_satisfied(clause: list[list[int]], x: int) -> bool:
    return any(((x >> var) & 1) == pos for var, pos in clause)


class SatGenerator(TaskGenerator):
    family = "3sat"
    tiers = (1, 2, 3, 4, 5)

    def generate(self, tier: int, seed: int) -> TaskInstance:
        params = TIER_PARAMS[tier]
        for sub in range(MAX_TRIES):
            rng = random.Random(stable_rng_seed(self.family, tier, seed, sub))
            n = rng.choice(params["n_choices"])
            lo, hi = params["m_range"]
            hi = (19 - n) if hi is None else hi
            m = rng.randint(lo, hi)
            clauses = self._draw_clauses(rng, n, m)
            if clauses is None:
                self._record_reject(tier, seed, sub, "duplicate_clauses")
                continue
            rolling = params.get("rolling", False)
            spec = {"n_vars": n, "clauses": clauses,
                    "encoding": "rolling" if rolling else "flags"}
            budget = (n + 1 + counter_width(m)) if rolling else (n + m + 1)
            inst = TaskInstance(
                task_id=f"3sat-{tier_label(tier)}-s{seed:04d}",
                family=self.family, tier=tier, seed=seed,
                problem_text="", formal_spec=spec,
                n_problem_qubits=n,
                max_total_qubits=budget,
                max_depth=0,
            )
            try:
                self._check_instance(inst, self.classical_solutions(inst))
            except GeneratorReject as e:
                self._record_reject(tier, seed, sub, e.reason)
                continue
            inst.problem_text = render_verbose(spec)
            return self.finalize(inst)
        raise RuntimeError(f"3sat T{tier} s{seed}: retries exhausted")

    @staticmethod
    def _draw_clauses(rng: random.Random, n: int, m: int):
        clauses, seen = [], set()
        for _ in range(m * 10):
            variables = sorted(rng.sample(range(n), 3))
            clause = [[v, rng.randint(0, 1)] for v in variables]
            key = tuple(map(tuple, clause))
            if key in seen:
                continue
            seen.add(key)
            clauses.append(clause)
            if len(clauses) == m:
                return clauses
        return None

    def classical_solutions(self, inst: TaskInstance) -> set[int]:
        n = inst.formal_spec["n_vars"]
        clauses = inst.formal_spec["clauses"]
        return {
            x for x in range(1 << n)
            if all(clause_satisfied(c, x) for c in clauses)
        }

    def reference_oracle(self, inst: TaskInstance) -> QuantumCircuit:
        n = inst.formal_spec["n_vars"]
        clauses = inst.formal_spec["clauses"]
        m = len(clauses)

        def clause_flag(qc, j, target):
            variables = [v for v, _ in clauses[j]]
            # all literals false <=> clause UNSAT; then X => flag=1 iff SAT
            unsat_pattern = [1 - pos for _, pos in clauses[j]]
            flag_on_pattern(qc, variables, unsat_pattern, target)
            qc.x(target)

        if inst.formal_spec.get("encoding") == "rolling":
            # zero-slack: one shared flag + clause counter, rolling reuse
            w = counter_width(m)
            qc = QuantumCircuit(n + 1 + w)
            flag = n
            counter = list(range(n + 1, n + 1 + w))
            for j in range(m):
                clause_flag(qc, j, flag)
                controlled_increment(qc, [flag], counter)
                clause_flag(qc, j, flag)
            phase_on_pattern(qc, counter, [(m >> i) & 1 for i in range(w)])
            for j in reversed(range(m)):
                clause_flag(qc, j, flag)
                controlled_decrement(qc, [flag], counter)
                clause_flag(qc, j, flag)
            return qc

        qc = QuantumCircuit(n + m)
        flags = list(range(n, n + m))

        def compute_flags():
            for j in range(m):
                clause_flag(qc, j, flags[j])

        compute_flags()
        phase_on_pattern(qc, flags, [1] * m)
        compute_flags()          # the flag block is an involution
        return qc


# ---- problem-text rendering -------------------------------------------------

def _fmt_clause(clause) -> str:
    return "(" + " OR ".join(
        ("x{}".format(v) if pos else "NOT x{}".format(v)) for v, pos in clause
    ) + ")"


def render_verbose(spec: dict) -> str:
    n, clauses = spec["n_vars"], spec["clauses"]
    lines = [
        f"We have a 3-SAT formula over {n} Boolean variables "
        f"x0, x1, ..., x{n-1}.",
        "Variable x_i is stored on problem_qubits[i] "
        "(basis value 1 means the variable is True).",
        "The formula is the AND of the following clauses:",
    ]
    lines += ["  " + _fmt_clause(c) for c in clauses]
    lines += [
        "",
        "The classical predicate is f(x) = 1 if and only if the assignment "
        "x = (x0, ..., x{}) satisfies every clause above.".format(n - 1),
    ]
    return "\n".join(lines)


def render_terse(spec: dict) -> str:
    n, clauses = spec["n_vars"], spec["clauses"]
    cl = " AND ".join(_fmt_clause(c) for c in clauses)
    return (f"3-SAT, n={n} vars (x_i on problem_qubits[i], 1=True). "
            f"f(x)=1 iff: {cl}")
