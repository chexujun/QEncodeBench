from qiskit import QuantumCircuit
import math


def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    pattern = "0101"
    n = 5
    offsets = [0, 1]

    match_anc = ancilla_qubits[0]
    out_anc = ancilla_qubits[1]

    or_flips = []

    for o in offsets:
        controls = []
        flipped = []
        for i, ch in enumerate(pattern):
            if ch == '?':
                continue
            q = problem_qubits[o + i]
            if ch == '0':
                qc.x(q)
                flipped.append(q)
            controls.append(q)

        qc.mcx(controls, match_anc)

        for q in flipped:
            qc.x(q)

        qc.cx(match_anc, out_anc)

        for q in flipped:
            qc.x(q)
        qc.mcx(controls, match_anc)
        for q in flipped:
            qc.x(q)
        or_flips.append(None)

    qc.z(out_anc)

    for o in reversed(offsets):
        controls = []
        flipped = []
        for i, ch in enumerate(pattern):
            if ch == '?':
                continue
            q = problem_qubits[o + i]
            if ch == '0':
                qc.x(q)
                flipped.append(q)
            controls.append(q)

        qc.mcx(controls, match_anc)
        qc.cx(match_anc, out_anc)
        qc.mcx(controls, match_anc)

        for q in flipped:
            qc.x(q)
