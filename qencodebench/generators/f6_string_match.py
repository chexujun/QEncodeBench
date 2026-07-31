"""F6: wildcard pattern matching over a binary text.

Encoding domain == problem domain: qubit i = text character s_i (0/1).
Pattern p is over {0, 1, ?}; '?' matches anything.

T1: anchored match (pattern length == text length, single offset).
T2/T3: substring match: f(x) = 1 iff the pattern matches at SOME offset.

Qubit account: T1: n + 2 (reference needs no ancilla; slack for models).
T2/T3: n + (n - L + 1) offset flags + 1.
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

MAX_TRIES = 800

TIER_PARAMS = {
    1: dict(n_choices=[4, 5, 6], anchored=True, wc_range=(0, 3)),
    2: dict(n_choices=[5, 6, 7], anchored=False, l_offset=(1, 2),
            wc_range=(0, 2)),
    3: dict(n_choices=[8], anchored=False, l_choices=[3, 4], wc_range=(0, 2)),
    # T3p: zero-slack rolling offset counter; T4: text length to n=12
    4: dict(n_choices=[7, 8], anchored=False, l_offset=(3, 5),
            wc_range=(0, 2), rolling=True),
    5: dict(n_choices=[10, 12], anchored=False, l_choices=[6, 7],
            wc_range=(0, 2)),
}


def matches_at(text_bits: int, pattern: str, offset: int) -> bool:
    return all(
        ch == "?" or ((text_bits >> (offset + i)) & 1) == int(ch)
        for i, ch in enumerate(pattern)
    )


def f_value(text_bits: int, pattern: str, n: int, anchored: bool) -> bool:
    if anchored:
        return matches_at(text_bits, pattern, 0)
    return any(matches_at(text_bits, pattern, o)
               for o in range(n - len(pattern) + 1))


class StringMatchGenerator(TaskGenerator):
    family = "string_match"
    tiers = (1, 2, 3, 4, 5)

    def generate(self, tier: int, seed: int) -> TaskInstance:
        params = TIER_PARAMS[tier]
        for sub in range(MAX_TRIES):
            rng = random.Random(stable_rng_seed(self.family, tier, seed, sub))
            n = rng.choice(params["n_choices"])
            anchored = params.get("anchored", False)
            if anchored:
                length = n
            elif "l_choices" in params:
                length = rng.choice(params["l_choices"])
            else:
                lo, hi = params["l_offset"]
                length = n - rng.randint(lo, hi)
            wc_lo, wc_hi = params["wc_range"]
            n_wc = rng.randint(wc_lo, min(wc_hi, length - 1))
            wc_pos = set(rng.sample(range(length), n_wc))
            pattern = "".join(
                "?" if i in wc_pos else str(rng.randint(0, 1))
                for i in range(length)
            )
            rolling = params.get("rolling", False)
            if anchored:
                budget = n + 2
            elif rolling:
                budget = n + 1 + counter_width(n - length + 1)
            else:
                budget = n + (n - length + 1) + 1
            if budget > GLOBAL_QUBIT_CAP:
                self._record_reject(tier, seed, sub, f"budget:{budget}")
                continue
            spec = {"n_text": n, "pattern": pattern, "anchored": anchored,
                    "encoding": "rolling" if rolling else "flags"}
            inst = TaskInstance(
                task_id=f"string_match-{tier_label(tier)}-s{seed:04d}",
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
        raise RuntimeError(f"string_match T{tier} s{seed}: retries exhausted")

    def classical_solutions(self, inst: TaskInstance) -> set[int]:
        n = inst.formal_spec["n_text"]
        pattern = inst.formal_spec["pattern"]
        anchored = inst.formal_spec["anchored"]
        return {x for x in range(1 << n) if f_value(x, pattern, n, anchored)}

    def reference_oracle(self, inst: TaskInstance) -> QuantumCircuit:
        n = inst.formal_spec["n_text"]
        pattern = inst.formal_spec["pattern"]
        anchored = inst.formal_spec["anchored"]
        fixed = [(i, int(ch)) for i, ch in enumerate(pattern) if ch != "?"]

        if anchored:
            qc = QuantumCircuit(n)
            phase_on_pattern(qc, [i for i, _ in fixed], [b for _, b in fixed])
            return qc

        n_off = n - len(pattern) + 1
        if inst.formal_spec.get("encoding") == "rolling":
            # zero-slack: shared match flag rolls into an offset counter;
            # f = (count >= 1) -> one phase per nonzero count value
            w = counter_width(n_off)
            qc = QuantumCircuit(n + 1 + w)
            flag = n
            counter = list(range(n + 1, n + 1 + w))

            def off_flag(o):
                flag_on_pattern(qc, [o + i for i, _ in fixed],
                                [b for _, b in fixed], flag)

            for o in range(n_off):
                off_flag(o)
                controlled_increment(qc, [flag], counter)
                off_flag(o)
            for v in range(1, n_off + 1):
                phase_on_pattern(qc, counter,
                                 [(v >> i) & 1 for i in range(w)])
            for o in reversed(range(n_off)):
                off_flag(o)
                controlled_decrement(qc, [flag], counter)
                off_flag(o)
            return qc

        qc = QuantumCircuit(n + n_off)
        flags = list(range(n, n + n_off))

        def compute():
            for o in range(n_off):
                flag_on_pattern(qc, [o + i for i, _ in fixed],
                                [b for _, b in fixed], flags[o])

        compute()
        # (-1)^(OR of flags): global -1, then -1 again on the no-match states
        qc.global_phase += 3.14159265358979323846
        phase_on_pattern(qc, flags, [0] * n_off)
        compute()                                    # involution
        return qc


# ---- problem-text rendering -------------------------------------------------

def render_verbose(spec: dict) -> str:
    n, pattern = spec["n_text"], spec["pattern"]
    kind = ("must match the text exactly, position by position"
            if spec["anchored"] else
            "must appear as a CONTIGUOUS substring at some offset")
    return "\n".join([
        f"We have a binary text of length {n}: s = s_0 s_1 ... s_{n-1}, "
        "where character s_i is stored on problem_qubits[i].",
        f"We are given a pattern of length {len(pattern)} over the alphabet "
        f"{{0, 1, ?}}:  pattern = \"{pattern}\" (read left to right, "
        "position 0 first).",
        "The wildcard '?' matches both 0 and 1.",
        f"The pattern {kind}.",
        "",
        "The classical predicate is f(x) = 1 if and only if the text "
        "encoded by x matches the pattern"
        + ("" if spec["anchored"] else
           f" at at least one offset o in 0..{n - len(pattern)} "
           f"(pattern position i is compared against s_(o+i))") + ".",
    ])


def render_terse(spec: dict) -> str:
    mode = "anchored (offset 0 only)" if spec["anchored"] else "any offset"
    return (f"Wildcard string match, text length {spec['n_text']} (s_i on "
            f"qubit i), pattern=\"{spec['pattern']}\" ('?' matches 0 and 1), "
            f"mode: {mode}. f(x)=1 iff pattern matches.")
