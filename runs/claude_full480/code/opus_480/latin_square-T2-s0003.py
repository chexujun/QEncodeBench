from qiskit import QuantumCircuit
import numpy as np

def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    # Free cells (row,col): j0=(0,1), j1=(1,0), j2=(2,2)
    # code bits: cell j low=problem_qubits[2j], high=problem_qubits[2j+1]
    # decode: 00->0, 01->1, 10->2, 11->0
    # value==0  iff  (b0,b1) in {00,11}  iff  b0==b1
    # value==1  iff  (b0,b1)==(1,0)      iff  b0 & ~b1
    # value==2  iff  (b0,b1)==(0,1)      iff  ~b0 & b1
    #
    # Grid:
    #   0 . 2      row0: given {0,2}, free (0,1) must be 1
    #   . 0 1      row1: given {0,1}, free (1,0) must be 2
    #   1 2 .      row2: given {1,2}, free (2,2) must be 0
    # Columns:
    #   col0: given rows0,2 = {0,1}, free (1,0) must be 2  (consistent)
    #   col1: given rows1,2 = {0,2}, free (0,1) must be 1  (consistent)
    #   col2: given rows0,1 = {2,1}, free (2,2) must be 0  (consistent)
    #
    # So f(x)=1  iff  cell0==1  AND  cell1==2  AND  cell2==0.

    b0_0, b1_0 = problem_qubits[0], problem_qubits[1]  # cell 0
    b0_1, b1_1 = problem_qubits[2], problem_qubits[3]  # cell 1
    b0_2, b1_2 = problem_qubits[4], problem_qubits[5]  # cell 2

    a0, a1, a2 = ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[2]

    # a0 = 1  iff cell0 == value 1 : (b0_0=1, b1_0=0)
    qc.x(b1_0)
    qc.ccx(b0_0, b1_0, a0)
    qc.x(b1_0)

    # a1 = 1  iff cell1 == value 2 : (b0_1=0, b1_1=1)
    qc.x(b0_1)
    qc.ccx(b0_1, b1_1, a1)
    qc.x(b0_1)

    # a2 = 1  iff cell2 == value 0 : (b0_2 == b1_2)
    # b0_2 XOR b1_2 == 0.  Compute XOR into a2, then flip: a2 = NOT(b0 xor b1)
    qc.cx(b0_2, a2)
    qc.cx(b1_2, a2)
    qc.x(a2)

    # phase -1 iff a0 & a1 & a2 all == 1
    qc.h(a2)
    qc.ccx(a0, a1, a2)
    qc.h(a2)

    # uncompute (mirror)
    qc.x(a2)
    qc.cx(b1_2, a2)
    qc.cx(b0_2, a2)

    qc.x(b0_1)
    qc.ccx(b0_1, b1_1, a1)
    qc.x(b0_1)

    qc.x(b1_0)
    qc.ccx(b0_0, b1_0, a0)
    qc.x(b1_0)
