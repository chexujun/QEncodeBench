import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    # a = [5, 3, 2], target T = 5. Subsets summing to 5: {5} -> x=001, {3,2} -> x=110.
    p0, p1, p2 = problem_qubits[0], problem_qubits[1], problem_qubits[2]
    anc = ancilla_qubits[0]

    # Term 1: x0=1, x1=0, x2=0  (select only element 5)
    qc.x(p1)
    qc.x(p2)
    qc.mcx([p0, p1, p2], anc)
    qc.z(anc)
    qc.mcx([p0, p1, p2], anc)
    qc.x(p2)
    qc.x(p1)

    # Term 2: x0=0, x1=1, x2=1  (select elements 3 and 2)
    qc.x(p0)
    qc.mcx([p0, p1, p2], anc)
    qc.z(anc)
    qc.mcx([p0, p1, p2], anc)
    qc.x(p0)
