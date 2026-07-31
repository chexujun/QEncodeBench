"""Statevector simulation helpers (Aer, CPU, hard cap 20 qubits)."""

from __future__ import annotations

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
import qiskit_aer  # noqa: F401  (registers set_statevector/save_statevector)

_SIM = AerSimulator(method="statevector")

SIM_QUBIT_CAP = 20


def run_statevector(circ: QuantumCircuit,
                    initial: np.ndarray | None = None) -> np.ndarray:
    """Return the statevector after applying ``circ`` to |0...0> or to the
    given initial statevector (length 2^num_qubits)."""
    if circ.num_qubits > SIM_QUBIT_CAP:
        raise ValueError(f"{circ.num_qubits} qubits exceeds cap {SIM_QUBIT_CAP}")
    def wrap(payload: QuantumCircuit) -> QuantumCircuit:
        qc = QuantumCircuit(circ.num_qubits)
        if initial is not None:
            qc.set_statevector(initial)
        qc.compose(payload, inplace=True)
        qc.save_statevector()
        return qc

    try:
        result = _SIM.run(wrap(circ)).result()
        sv = result.get_statevector()
    except Exception:
        # Fall back to transpiling exotic gates into Aer's basis.
        # Transpile ONLY the payload circuit: set_statevector must never
        # enter the optimizer -- passes can commute/merge diagonal phase
        # gates across the state injection, silently corrupting per-basis
        # phases (nondeterministically).  A payload-only transpile is a
        # plain unitary-equivalence rewrite (global phase tracked), so the
        # default optimization level is safe; the seed pins determinism.
        # The Aer form is cached on the circuit object: exhaustive() calls
        # this 2^n times with the same payload.
        tqc = getattr(circ, "_qeb_aer_form", None)
        if tqc is None:
            tqc = transpile(circ, _SIM, seed_transpiler=0)
            try:
                circ._qeb_aer_form = tqc
            except Exception:
                pass
        sv = _SIM.run(wrap(tqc)).result().get_statevector()
    return np.asarray(sv)


def basis_state(index: int, n_qubits: int) -> np.ndarray:
    v = np.zeros(1 << n_qubits, dtype=complex)
    v[index] = 1.0
    return v
