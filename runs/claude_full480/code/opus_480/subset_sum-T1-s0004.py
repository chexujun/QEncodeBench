from qiskit import QuantumCircuit
from math import pi

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # a = [5, 4, 3], target T = 8. Subsets summing to 8: {5,3} -> bits x0,x2 ; {4} alone? 4!=8 ; {5,4,3}=12 ; {4,3}=7 ; {5,4}=9 ; {5}=5 ; {3}=3 ; {} =0.
    # Only solution: x0=1, x2=1, x1=0  (5+3=8).
    p0, p1, p2 = problem_qubits[0], problem_qubits[1], problem_qubits[2]
    anc = ancilla_qubits[0]

    # compute predicate: x0 AND (NOT x1) AND x2 into ancilla
    qc.x(p1)                     # NOT x1
    qc.ccx(p0, p1, anc)          # anc = x0 AND (NOT x1)
    qc.ccx(p2, anc, ancilla_qubits[1])  # anc2 = anc AND x2
    qc.z(ancilla_qubits[1])      # phase flip when predicate holds
    qc.ccx(p2, anc, ancilla_qubits[1])  # uncompute anc2
    qc.ccx(p0, p1, anc)          # uncompute anc
    qc.x(p1)                     # restore x1
