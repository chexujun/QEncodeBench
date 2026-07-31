import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a = [8, 1, 5, 8]
    T = 1
    # Solutions: subsets summing to 1. Only a[1]=1 works => select only index 1.
    # f(x)=1 iff x1=1 and x0=x2=x3=0.
    q = problem_qubits
    # Flip the zero-bits so that the marked pattern maps to all-ones.
    qc.x(q[0])
    qc.x(q[2])
    qc.x(q[3])
    # Phase -1 iff all four qubits are 1 (pattern q0=0,q1=1,q2=0,q3=0).
    qc.h(q[3])
    qc.mcx([q[0], q[1], q[2]], q[3])
    qc.h(q[3])
    # Uncompute the flips.
    qc.x(q[0])
    qc.x(q[2])
    qc.x(q[3])
