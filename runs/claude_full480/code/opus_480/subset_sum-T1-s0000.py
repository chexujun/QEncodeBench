from qiskit import QuantumCircuit
import numpy as np


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # a = [1, 5, 5], target T = 6.
    # Subsets summing to 6: {1,5} using a[0]+a[1], and {1,5} using a[0]+a[2].
    # x0 selects a[0]=1, x1 selects a[1]=5, x2 selects a[2]=5.
    # Sum = x0*1 + x1*5 + x2*5 = 6  <=>  x0=1 and (x1 + x2)*5 = 5
    #   => x0=1 and exactly one of x1,x2 is 1.
    # f(x)=1 iff x0=1 AND (x1 XOR x2)=1.
    p0, p1, p2 = problem_qubits[0], problem_qubits[1], problem_qubits[2]
    a = ancilla_qubits[0]

    # compute: a = x1 XOR x2
    qc.cx(p1, a)
    qc.cx(p2, a)
    # phase -1 iff (x0=1 AND a=1)
    qc.cz(p0, a)
    # uncompute
    qc.cx(p2, a)
    qc.cx(p1, a)
