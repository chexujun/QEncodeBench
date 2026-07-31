import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # a = [1, 1, 5], target T = 6.
    # Subsets summing to 6: 1 + 5 (x0,x2) or 1 + 5 (x1,x2).
    # So f(x)=1 iff x2==1 AND exactly one of x0,x1 is 1.
    p0, p1, p2 = problem_qubits[0], problem_qubits[1], problem_qubits[2]
    anc = ancilla_qubits[0]

    # Compute XOR of x0 and x1 into ancilla (1 iff exactly one selected).
    qc.cx(p0, anc)
    qc.cx(p1, anc)

    # Phase -1 iff (x2 == 1) AND (anc == 1).
    qc.cz(p2, anc)

    # Uncompute ancilla.
    qc.cx(p1, anc)
    qc.cx(p0, anc)
