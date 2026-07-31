from qiskit import QuantumCircuit
import numpy as np


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Free cells (row,col): 0->(0,0), 1->(1,2), 2->(2,1)
    # Given grid:
    #   . 0 2
    #   2 1 .
    #   0 . 1
    # Free cell j uses b0=problem_qubits[2j], b1=problem_qubits[2j+1], code c=b0+2*b1.
    # Decode: 00->0, 01->1, 10->2, 11->0.
    # value==0 iff (b0==0 and b1==0) or (b0==1 and b1==1) i.e. b0==b1
    # value==1 iff b0==1 and b1==0
    # value==2 iff b0==0 and b1==1
    #
    # Constraints to satisfy (Latin square), given fixed cells:
    # Cell0 (0,0): row0 has {0,2}, needs value 1. col0 has {2,0}, needs value 1.
    #   => Cell0 value must be 1.  value1 iff b0==1,b1==0.
    # Cell1 (1,2): row1 has {2,1}, needs value 0. col2 has {2,1}, needs value 0.
    #   => Cell1 value must be 0.  value0 iff b0==b1.
    # Cell2 (2,1): row2 has {0,1}, needs value 2. col1 has {0,1}, needs value 2.
    #   => Cell2 value must be 2.  value2 iff b0==0,b1==1.
    #
    # f(x)=1 iff  cell0=value1 AND cell1=value0 AND cell2=value2.

    b0_0, b1_0 = problem_qubits[0], problem_qubits[1]
    b0_1, b1_1 = problem_qubits[2], problem_qubits[3]
    b0_2, b1_2 = problem_qubits[4], problem_qubits[5]

    p0 = ancilla_qubits[0]  # cell0 == value1
    p1 = ancilla_qubits[1]  # cell1 == value0
    p2 = ancilla_qubits[2]  # cell2 == value2
    t1 = ancilla_qubits[3]  # helper for cell1 equality
    flag = ancilla_qubits[4]

    # --- compute p0: cell0 value==1  <=> b0_0==1 and b1_0==0 ---
    qc.x(b1_0)
    qc.ccx(b0_0, b1_0, p0)
    qc.x(b1_0)

    # --- compute p1: cell1 value==0 <=> b0_1==b1_1 ---
    # equality: t1 = 1 iff b0_1==b1_1.  t1 = NOT(b0_1 xor b1_1)
    qc.cx(b0_1, t1)
    qc.cx(b1_1, t1)
    qc.x(t1)   # t1 = 1 iff equal
    # copy into p1
    qc.cx(t1, p1)

    # --- compute p2: cell2 value==2 <=> b0_2==0 and b1_2==1 ---
    qc.x(b0_2)
    qc.ccx(b0_2, b1_2, p2)
    qc.x(b0_2)

    # --- combine: flag = p0 AND p1 AND p2 ---
    qc.ccx(p0, p1, flag)
    # phase -1 iff flag AND p2
    qc.cz(flag, p2)
    # uncompute flag
    qc.ccx(p0, p1, flag)

    # --- uncompute p2 ---
    qc.x(b0_2)
    qc.ccx(b0_2, b1_2, p2)
    qc.x(b0_2)

    # --- uncompute p1 ---
    qc.cx(t1, p1)
    qc.x(t1)
    qc.cx(b1_1, t1)
    qc.cx(b0_1, t1)

    # --- uncompute p0 ---
    qc.x(b1_0)
    qc.ccx(b0_0, b1_0, p0)
    qc.x(b1_0)
