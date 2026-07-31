"""Core task types: TaskInstance dataclass and TaskGenerator ABC.

Conventions used throughout the project:
  - Problem qubits are circuit indices [0, n_problem); ancillas follow.
  - A variable assignment is encoded as an integer x where bit i (little-endian,
    Qiskit convention) is the value of variable/qubit i.  The statevector index
    of basis state |x>|0...0>_anc is therefore exactly x.
  - classical_solutions returns the set of satisfying assignments as ints.
"""

from __future__ import annotations

import hashlib
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from qiskit import QuantumCircuit

GLOBAL_QUBIT_CAP = 20

# (frozen_v1.1)
TIER_LABELS = {1: "T1", 2: "T2", 3: "T3", 4: "T3p", 5: "T4"}


def tier_label(tier: int) -> str:
    return TIER_LABELS[tier]
# Solution density must lie in [MIN_DENSITY, MAX_DENSITY].
MIN_DENSITY = 1 / 64
MAX_DENSITY = 1 / 2

INTERFACE_CONTRACT = (
    "def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], "
    "ancilla_qubits: list[int]) -> None"
)


@dataclass
class TaskInstance:
    task_id: str            # e.g. "3sat-T2-s0042"
    family: str
    tier: int               # 1 | 2 | 3
    seed: int
    problem_text: str       # natural-language statement (rendered template)
    formal_spec: dict       # machine-readable constraints
    n_problem_qubits: int
    max_total_qubits: int   # per-instance family-formula budget, <= 20
    max_depth: int          # transpiled-depth budget (4x reference)
    interface_contract: str = INTERFACE_CONTRACT
    ref_qubits: int = 0     # qubits actually touched by the reference oracle
    ref_depth: int = 0      # transpiled depth of the reference oracle

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False, sort_keys=True)

    @classmethod
    def from_dict(cls, d: dict) -> "TaskInstance":
        return cls(**d)


class GeneratorReject(Exception):
    """Raised when a candidate instance fails a validity filter."""

    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(reason)


def stable_rng_seed(family: str, tier: int, seed: int, salt: int = 0) -> int:
    """Deterministic cross-process RNG seed for (family, tier, seed)."""
    key = f"{family}|{tier}|{seed}|{salt}".encode()
    return int.from_bytes(hashlib.sha256(key).digest()[:8], "big")


def density_ok(n_solutions: int, n_qubits: int) -> bool:
    total = 1 << n_qubits
    return MIN_DENSITY <= n_solutions / total <= MAX_DENSITY


class TaskGenerator(ABC):
    """Uniform generator interface.

    ``tiers`` lists the tiers this family supports (frozen_v1.1 adds
    4 = T3p zero-slack rolling budget and 5 = T4 scale-up where the
    yield rules permit).

    generate() must be deterministic: identical (family, tier, seed) always
    produce the identical instance.  Internally a generator may iterate over
    sub-seeded candidates until validity filters pass; the iteration itself is
    seed-deterministic.  Filter rejections are reported via the ``rejects``
    list so callers can log them to generator_rejects.log.
    """

    family: str
    tiers: tuple = (1, 2, 3)

    def __init__(self) -> None:
        self.rejects: list[dict] = []

    @abstractmethod
    def generate(self, tier: int, seed: int) -> TaskInstance:
        ...

    @abstractmethod
    def reference_oracle(self, inst: TaskInstance) -> "QuantumCircuit":
        """Golden phase oracle on n_problem + n_ref_ancilla qubits."""

    @abstractmethod
    def classical_solutions(self, inst: TaskInstance) -> set[int]:
        """Brute-force satisfying assignments over 2^n_problem codes."""

    # ---- shared helpers -------------------------------------------------

    def finalize(self, inst: TaskInstance) -> TaskInstance:
        """Fill reference-implementation stats and the depth budget.

        Called once per accepted instance (after all validity filters).
        Also asserts the qubit account: reference total <= family budget.
        """
        from qencodebench.core.transpiling import transpile_fixed

        ref = self.reference_oracle(inst)
        if ref.num_qubits > inst.max_total_qubits:
            raise GeneratorReject(
                f"reference_overflows_budget:{ref.num_qubits}>"
                f"{inst.max_total_qubits}")
        tqc = transpile_fixed(ref)
        inst.ref_qubits = ref.num_qubits
        inst.ref_depth = tqc.depth()
        inst.max_depth = 4 * tqc.depth()
        return inst

    def _record_reject(self, tier: int, seed: int, sub: int, reason: str) -> None:
        self.rejects.append(
            {"family": self.family, "tier": tier, "seed": seed,
             "candidate": sub, "reason": reason}
        )

    def _check_instance(self, inst: TaskInstance, solutions: set[int]) -> None:
        """Common validity filters; raises GeneratorReject on failure."""
        n = inst.n_problem_qubits
        total = 1 << n
        if not solutions:
            raise GeneratorReject("empty_solution_set")
        if len(solutions) == total:
            raise GeneratorReject("full_solution_set")
        if not density_ok(len(solutions), n):
            raise GeneratorReject(
                f"density_out_of_range:{len(solutions)}/{total}")
        if inst.max_total_qubits > GLOBAL_QUBIT_CAP:
            raise GeneratorReject(
                f"budget_exceeds_cap:{inst.max_total_qubits}")
