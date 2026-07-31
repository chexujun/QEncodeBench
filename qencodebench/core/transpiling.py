"""Fixed transpile configuration.

The triple (basis_gates, optimization_level, qiskit version) is part of the
verifier_version semantics: any change bumps VERIFIER_VERSION and requires
full re-verification.
"""

from __future__ import annotations

from qiskit import QuantumCircuit, transpile

BASIS_GATES = ["rz", "sx", "x", "cx"]
OPT_LEVEL = 1


def transpile_fixed(circ: QuantumCircuit) -> QuantumCircuit:
    return transpile(circ, basis_gates=BASIS_GATES,
                     optimization_level=OPT_LEVEL)
