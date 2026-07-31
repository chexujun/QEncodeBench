from qiskit import QuantumCircuit
import numpy as np


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Free cells (row,col): j0=(0,0), j1=(0,1), j2=(2,0), j3=(2,2)
    # Value code per cell j: b0=problem_qubits[2j], b1=problem_qubits[2j+1]
    # Decode: 00->0, 01->1, 10->2, 11->0 (surjective)
    # Grid givens:
    #  row0: [c0, c1, 2]      col0: [c0, 2, c2]
    #  row1: [2, 1, 0]        col1: [c1, 1, 2]
    #  row2: [c2, 2, c3]      col2: [2, 0, c3]
    #
    # Constraints for a valid Latin square (each row/col = {0,1,2}):
    # row0: {c0,c1,2} all-different -> c0,c1 in {0,1}, c0 != c1
    # row2: {c2,2,c3} all-different -> c2,c3 in {0,1}, c2 != c3
    # col0: {c0,2,c2} all-different -> c0,c2 in {0,1}, c0 != c2
    # col1: {c1,1,2} all-different -> c1 == 0
    # col2: {2,0,c3} all-different -> c3 == 1
    #
    # Solve: c1=0 => c0=1 (row0). c0=1 => c2=0 (col0). c3=1 => c2=0 (row2) consistent.
    # Unique solution: c0=1, c1=0, c2=0, c3=1.
    #
    # value(cell) meanings via codes:
    #   c==0 : code 00 or 11
    #   c==1 : code 01
    #   c==2 : code 10
    # We need predicate: cell0==1, cell1==0, cell2==0, cell3==1.
    #
    # Helpers on (b0,b1) with b0 low, b1 high:
    #   is_val1  (code 01): b0=1, b1=0
    #   is_val0  (code 00 or 11): b0==b1
    #
    # cell0==1: p0b0=1, p0b1=0
    # cell1==0: p1b0==p1b1
    # cell2==0: p2b0==p2b1
    # cell3==1: p3b0=1, p3b1=0

    p0b0, p0b1 = problem_qubits[0], problem_qubits[1]
    p1b0, p1b1 = problem_qubits[2], problem_qubits[3]
    p2b0, p2b1 = problem_qubits[4], problem_qubits[5]
    p3b0, p3b1 = problem_qubits[6], problem_qubits[7]

    a0, a1, a2, a3 = ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[2], ancilla_qubits[3]

    # a0 = 1 iff cell0 == value 1  (b0=1 AND b1=0)
    qc.x(p0b1)
    qc.ccx(p0b0, p0b1, a0)
    qc.x(p0b1)

    # a3 = 1 iff cell3 == value 1  (b0=1 AND b1=0)
    qc.x(p3b1)
    qc.ccx(p3b0, p3b1, a3)
    qc.x(p3b1)

    # a1 = 1 iff cell1 == value 0  (b0 == b1)  -> a1 = NOT(b0 xor b1)
    qc.cx(p1b0, a1)
    qc.cx(p1b1, a1)
    qc.x(a1)

    # a2 = 1 iff cell2 == value 0  (b0 == b1)
    qc.cx(p2b0, a2)
    qc.cx(p2b1, a2)
    qc.x(a2)

    # phase -1 iff a0 AND a1 AND a2 AND a3
    qc.h(a3)
    qc.mcx([a0, a1, a2], a3)
    qc.h(a3)

    # uncompute a2
    qc.x(a2)
    qc.cx(p2b1, a2)
    qc.cx(p2b0, a2)

    # uncompute a1
    qc.x(a1)
    qc.cx(p1b1, a1)
    qc.cx(p1b0, a1)

    # uncompute a3
    qc.x(p3b1)
    qc.ccx(p3b0, p3b1, a3)
    qc.x(p3b1)

    # uncompute a0
    qc.x(p0b1)
    qc.ccx(p0b0, p0b1, a0)
    qc.x(p0b1)
