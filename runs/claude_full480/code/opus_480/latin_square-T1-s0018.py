from qiskit import QuantumCircuit
import math


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Grid:
    #   row0: 0 1 2
    #   row1: 1 2 A   (A = free cell 0, code = q0 low, q1 high)
    #   row2: 2 0 B   (B = free cell 1, code = q2 low, q3 high)
    #
    # Decoding (surjective): 00->0, 01->1, 10->2, 11->0.
    # Constraints for a valid Latin square:
    #   A must be 0 (row1 has {1,2}, col2 has {2}); so A in {0} -> value 0.
    #   B must be 1 (row2 has {2,0}, col2 has {2, A}); B must complete col2.
    # Column2 = {2, A, B} must be {0,1,2}; with A=0 needed for row1,
    # col2 = {2,0,B} => B=1. Row2 = {2,0,B} => B=1. Consistent.
    #
    # So f(x)=1 iff value(A)==0 AND value(B)==1.
    # value(A)==0  <=> code A in {00, 11}  <=> (a0 == a1)
    # value(B)==1  <=> code B == 01         <=> (b0==1 and b1==0)

    a0 = problem_qubits[0]
    a1 = problem_qubits[1]
    b0 = problem_qubits[2]
    b1 = problem_qubits[3]

    anc_A = ancilla_qubits[0]  # =1 iff value(A)==0
    anc_B = ancilla_qubits[1]  # =1 iff value(B)==1

    # value(A)==0 iff a0 == a1 iff NOT(a0 XOR a1)
    qc.cx(a0, anc_A)
    qc.cx(a1, anc_A)
    qc.x(anc_A)  # anc_A = 1 iff a0==a1

    # value(B)==1 iff b0==1 and b1==0
    qc.x(b1)
    qc.ccx(b0, b1, anc_B)  # anc_B = b0 AND (not b1)
    qc.x(b1)

    # phase -1 iff anc_A and anc_B both 1
    qc.cz(anc_A, anc_B)

    # uncompute
    qc.x(b1)
    qc.ccx(b0, b1, anc_B)
    qc.x(b1)

    qc.x(anc_A)
    qc.cx(a1, anc_A)
    qc.cx(a0, anc_A)
