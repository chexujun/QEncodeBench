"""F4: subset sum via a reversible constant adder and comparator.

Encoding domain == problem domain: qubit i = element i selected.
f(x) = 1 iff sum of the selected elements equals target T.

Qubit account: e elements + sum register ceil(log2(sum(a)+1)).
Budget formula: e + width(sum(a)).
"""

from __future__ import annotations

import random

from qiskit import QuantumCircuit

from qencodebench.core.task import (
    TaskInstance, TaskGenerator, GeneratorReject, stable_rng_seed,
    GLOBAL_QUBIT_CAP, tier_label,
)
from qencodebench.core.circuits import (
    controlled_add_const, controlled_sub_const, phase_on_pattern,
    counter_width,
)

MAX_TRIES = 500

TIER_PARAMS = {
    1: dict(n_elements=3, value_range=(1, 6)),
    2: dict(n_elements=4, value_range=(1, 10)),
    3: dict(n_elements=5, value_range=(2, 15)),
    # T4 scale-up: more/larger elements (sum register widens; e + w <= 20).
    # T3p N/A -- the sum register is information-theoretically irreducible
    5: dict(n_elements=[6, 7, 8], value_range=(3, 40)),
}


class SubsetSumGenerator(TaskGenerator):
    family = "subset_sum"
    tiers = (1, 2, 3, 5)

    def generate(self, tier: int, seed: int) -> TaskInstance:
        params = TIER_PARAMS[tier]
        for sub in range(MAX_TRIES):
            rng = random.Random(stable_rng_seed(self.family, tier, seed, sub))
            e = params["n_elements"]
            if isinstance(e, list):
                e = rng.choice(e)
            lo, hi = params["value_range"]
            values = [rng.randint(lo, hi) for _ in range(e)]
            # target from a random non-empty subset -> at least one solution
            subset = rng.sample(range(e), rng.randint(1, e - 1))
            target = sum(values[i] for i in subset)
            w = counter_width(sum(values))
            budget = e + w
            if budget > GLOBAL_QUBIT_CAP:
                self._record_reject(tier, seed, sub, f"budget:{budget}")
                continue
            spec = {"values": values, "target": target}
            inst = TaskInstance(
                task_id=f"subset_sum-{tier_label(tier)}-s{seed:04d}",
                family=self.family, tier=tier, seed=seed,
                problem_text="", formal_spec=spec,
                n_problem_qubits=e,
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
        raise RuntimeError(f"subset_sum T{tier} s{seed}: retries exhausted")

    def classical_solutions(self, inst: TaskInstance) -> set[int]:
        values = inst.formal_spec["values"]
        target = inst.formal_spec["target"]
        e = len(values)
        return {
            x for x in range(1 << e)
            if sum(values[i] for i in range(e) if (x >> i) & 1) == target
        }

    def reference_oracle(self, inst: TaskInstance) -> QuantumCircuit:
        values = inst.formal_spec["values"]
        target = inst.formal_spec["target"]
        e = len(values)
        w = counter_width(sum(values))
        qc = QuantumCircuit(e + w)
        sumreg = list(range(e, e + w))

        for i, a in enumerate(values):
            controlled_add_const(qc, [i], sumreg, a)
        phase_on_pattern(qc, sumreg, [(target >> i) & 1 for i in range(w)])
        for i, a in enumerate(values):
            controlled_sub_const(qc, [i], sumreg, a)
        return qc


# ---- problem-text rendering -------------------------------------------------

def render_verbose(spec: dict) -> str:
    values, target = spec["values"], spec["target"]
    e = len(values)
    return "\n".join([
        f"We have {e} positive integers: a = {values}.",
        f"Qubit i (problem_qubits[i]) encodes whether element a[{'i'}] is "
        "selected (1 = selected).",
        "",
        f"The classical predicate is f(x) = 1 if and only if the sum of the "
        f"selected elements equals the target T = {target}.",
        "For example, f(x) = 1 when the bits of x select a subset of a "
        f"whose values add up to exactly {target}; otherwise f(x) = 0.",
    ])


def render_terse(spec: dict) -> str:
    return (f"Subset sum, a={spec['values']}, T={spec['target']}. Qubit i = "
            f"element i selected. f(x)=1 iff sum of selected = T.")
