from qiskit import QuantumCircuit
import math

def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    pattern = "101000"
    offsets = [0, 1]

    def apply_match_flip(offset, target):
        # Compute AND over pattern positions comparing pattern[i] to s[offset+i].
        # For pattern bit '1': control on qubit directly.
        # For pattern bit '0': control on NOT of qubit (X sandwich).
        # '?': skip.
        ctrl = []
        flips = []
        for i, pc in enumerate(pattern):
            if pc == '?':
                continue
            q = problem_qubits[offset + i]
            ctrl.append(q)
            if pc == '0':
                flips.append(q)
        for q in flips:
            qc.x(q)
        qc.mcx(ctrl, target)
        for q in flips:
            qc.x(q)

    a0 = ancilla_qubits[0]  # match flag for offset 0
    a1 = ancilla_qubits[1]  # match flag for offset 1
    a2 = ancilla_qubits[2]  # OR result

    # Compute per-offset match flags
    apply_match_flip(0, a0)
    apply_match_flip(1, a1)

    # OR: a2 = a0 OR a1 = NOT(NOT a0 AND NOT a1)
    qc.x(a0)
    qc.x(a1)
    qc.x(a2)
    qc.ccx(a0, a1, a2)  # a2 = 1 XOR (na0 AND na1) = OR(a0,a1)
    qc.x(a0)
    qc.x(a1)

    # Phase flip when a2 == 1
    qc.z(a2)

    # Uncompute OR
    qc.x(a0)
    qc.x(a1)
    qc.ccx(a0, a1, a2)
    qc.x(a2)
    qc.x(a0)
    qc.x(a1)

    # Uncompute match flags (mirror)
    apply_match_flip(1, a1)
    apply_match_flip(0, a0)
