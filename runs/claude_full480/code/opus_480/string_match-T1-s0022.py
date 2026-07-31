from qiskit import QuantumCircuit
import math

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    pattern = "0001?"
    fixed = [(i, int(c)) for i, c in enumerate(pattern) if c != '?']
    ctrl_qubits = []
    for i, bit in fixed:
        q = problem_qubits[i]
        if bit == 0:
            qc.x(q)
        ctrl_qubits.append(q)
    if len(ctrl_qubits) == 1:
        qc.z(ctrl_qubits[0])
    else:
        qc.h(ctrl_qubits[-1])
        qc.mcx(ctrl_qubits[:-1], ctrl_qubits[-1], ancilla_qubits[0], mode='recursion')
        qc.h(ctrl_qubits[-1])
    for i, bit in fixed:
        if bit == 0:
            qc.x(problem_qubits[i])
