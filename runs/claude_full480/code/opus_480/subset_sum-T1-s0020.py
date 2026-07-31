import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    # a = [4, 6, 3], target T = 9.
    # Subsets summing to 9: {6,3} -> select a[1],a[2]; {4,3} is 7, {4,6} is 10,
    # {4,6,3}=13, {4}=4,{6}=6,{3}=3, {} = 0.
    # Only subset summing to 9 is {6, 3} = a[1] + a[2].
    # So f(x) = 1 iff x1 = 1 AND x2 = 1 AND x0 = 0.
    q0, q1, q2 = problem_qubits[0], problem_qubits[1], problem_qubits[2]
    a = ancilla_qubits[0]
    # compute predicate: (NOT x0) AND x1 AND x2 into ancilla a
    qc.x(q0)                      # a-condition uses x0 == 0
    qc.mcx([q0, q1, q2], a)       # a = (x0==0? via flipped) & x1 & x2
    qc.x(q0)                      # restore q0
    qc.z(a)                       # phase -1 iff predicate holds
    qc.x(q0)
    qc.mcx([q0, q1, q2], a)       # uncompute
    qc.x(q0)
