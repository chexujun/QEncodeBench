from qiskit import QuantumCircuit
import math


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Free cells (row,col): 0->(0,2), 1->(1,1), 2->(2,0)
    # Grid givens:
    #   2 0 A
    #   0 B 2
    #   C 2 0
    # A=cell0, B=cell1, C=cell2
    # Codes: 00->0, 01->1, 10->2, 11->0
    # Constraints for a valid Latin square:
    #  Row0: {2,0,A} distinct -> A in {1}  (must be 1)
    #  Row1: {0,B,2} distinct -> B == 1
    #  Row2: {C,2,0} distinct -> C == 1
    #  Col0: {2,0,C} distinct -> C == 1
    #  Col1: {0,B,2} distinct -> B == 1
    #  Col2: {A,2,0} distinct -> A == 1
    # So valid iff A==1 and B==1 and C==1.
    # value(cell)==1 iff code==01 iff b0==1 and b1==0.

    def b0(j):
        return problem_qubits[2 * j]

    def b1(j):
        return problem_qubits[2 * j + 1]

    # We need predicate = AND over j in {0,1,2} of (b0[j]==1 AND b1[j]==0).
    # Flip b1[j] so that "b1==0" becomes control-1.
    for j in range(3):
        qc.x(b1(j))

    controls = [b0(0), b1(0), b0(1), b1(1), b0(2), b1(2)]
    target = ancilla_qubits[0]

    qc.mcx(controls, target, ancilla_qubits[1:], mode='v-chain')
    qc.z(target)
    qc.mcx(controls, target, ancilla_qubits[1:], mode='v-chain')

    for j in range(3):
        qc.x(b1(j))
