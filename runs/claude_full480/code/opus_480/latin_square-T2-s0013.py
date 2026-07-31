from qiskit import QuantumCircuit
import numpy as np


def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    # Free cells (row,col): j=0 -> (0,1), j=1 -> (0,2), j=2 -> (1,2)
    # Codes (b0=problem_qubits[2j], b1=problem_qubits[2j+1]):
    #   00->0, 01->1, 10->2, 11->0
    # Grid givens:
    #   row0: [1, F0, F1]      row1: [2, 0, F2]      row2: [0,1,2]
    #   col0: [1,2,0] col1: [F0,0,1] col2: [F1,F2,2]
    #
    # Constraints for a valid Latin square (rows/cols each a permutation of 0,1,2):
    #   Row0: {1, val(F0), val(F1)} = {0,1,2}
    #   Row1: {2, 0, val(F2)} = {0,1,2}  => val(F2) = 1
    #   Col1: {val(F0), 0, 1} = {0,1,2}  => val(F0) = 2
    #   Col2: {val(F1), val(F2), 2} = {0,1,2}
    # From F2=1 and F0=2: Row0 needs val(F1) = 0 (since {1,2,val(F1)} must be {0,1,2}).
    # Col2: {val(F1), 1, 2} = {0,1,2} => val(F1)=0. Consistent.
    # So the UNIQUE solution in VALUES: F0=2, F1=0, F2=1.
    #
    # Now map values to codes (surjective decode):
    #   val 2 <- code 10 only            => F0: b0=0, b1=1
    #   val 1 <- code 01 only            => F2: b0=1, b1=0
    #   val 0 <- code 00 or code 11      => F1: (b0=0,b1=0) OR (b0=1,b1=1) i.e. b0==b1
    #
    # Predicate f(x)=1 iff:
    #   F0: q0==0 and q1==1
    #   F1: q2==q3
    #   F2: q4==1 and q5==0
    # where q0=problem_qubits[0],...,q5=problem_qubits[5].

    q0, q1, q2, q3, q4, q5 = (problem_qubits[0], problem_qubits[1],
                              problem_qubits[2], problem_qubits[3],
                              problem_qubits[4], problem_qubits[5])

    # Ancilla layout
    aF0 = ancilla_qubits[0]   # F0 condition: q0==0 & q1==1
    aF1 = ancilla_qubits[1]   # F1 condition: q2==q3
    aF2 = ancilla_qubits[2]   # F2 condition: q4==1 & q5==0
    aeq = ancilla_qubits[3]   # helper for q2 xor q3

    # --- Compute F0: (NOT q0) AND q1 ---
    qc.x(q0)
    qc.ccx(q0, q1, aF0)
    qc.x(q0)

    # --- Compute F1: q2 == q3  ->  NOT(q2 xor q3) ---
    qc.cx(q2, aeq)
    qc.cx(q3, aeq)
    qc.x(aeq)          # aeq = 1 iff q2==q3
    qc.cx(aeq, aF1)    # copy into aF1
    # (aeq left; uncomputed later)

    # --- Compute F2: q4 AND (NOT q5) ---
    qc.x(q5)
    qc.ccx(q4, q5, aF2)
    qc.x(q5)

    # --- Phase: -1 iff aF0 & aF1 & aF2 all 1 ---
    qc.h(aF2)
    qc.ccx(aF0, aF1, aF2)   # combined with h gives CCZ-style phase on aF2
    qc.h(aF2)

    # --- Uncompute F2 ---
    qc.x(q5)
    qc.ccx(q4, q5, aF2)
    qc.x(q5)

    # --- Uncompute F1 ---
    qc.cx(aeq, aF1)
    qc.x(aeq)
    qc.cx(q3, aeq)
    qc.cx(q2, aeq)

    # --- Uncompute F0 ---
    qc.x(q0)
    qc.ccx(q0, q1, aF0)
    qc.x(q0)
