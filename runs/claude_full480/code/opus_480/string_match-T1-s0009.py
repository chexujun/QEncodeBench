from qiskit import QuantumCircuit
import math


def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    pattern = "100101"
    a = ancilla_qubits[0]

    fixed = [(i, int(c)) for i, c in enumerate(pattern) if c != '?']

    flipped = []
    for i, bit in fixed:
        if bit == 0:
            qc.x(problem_qubits[i])
            flipped.append(i)

    ctrl = [problem_qubits[i] for i, _ in fixed]

    qc.h(a)
    qc.mcx(ctrl, a)
    qc.h(a)

    for i in flipped:
        qc.x(problem_qubits[i])
