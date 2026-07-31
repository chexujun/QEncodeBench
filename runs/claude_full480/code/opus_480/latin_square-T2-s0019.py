from qiskit import QuantumCircuit
import numpy as np


def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    # Free cells: j0=(0,0), j1=(0,2), j2=(2,2)
    # Grid givens:
    #   row0: (0,0)=free0, (0,1)=1, (0,2)=free1
    #   row1: 1 0 2
    #   row2: (2,0)=0, (2,1)=2, (2,2)=free2
    # Columns:
    #   col0: free0, 1, 0
    #   col1: 1, 0, 2  (already valid)
    #   col2: free1, 2, free2
    #
    # Decode (b0,b1): 00->0, 01->1, 10->2, 11->0.
    # value == 0  iff (b0,b1) in {00, 11}  iff b0 == b1
    # value == 1  iff (b0,b1) == (1,0)     iff b0 & ~b1
    # value == 2  iff (b0,b1) == (0,1)     iff ~b0 & b1
    #
    # Constraints for a valid Latin square:
    #  free0 (0,0): row0 has given 1 -> free0 != 1 ; col0 has givens {1,0} -> free0 != 1, free0 != 0
    #               => free0 == 2
    #  free1 (0,2): row0 has given 1 and free0; col2 has given 2 and free2
    #  free2 (2,2): row2 has givens {0,2} -> free2 != 0, free2 != 2 => free2 == 1
    #  Then row0 = {free0, 1, free1} must be all-different, col2={free1,2,free2} all-diff.
    #  With free0=2, free2=1:
    #    row0: {2,1,free1} distinct => free1 == 0
    #    col2: {free1,2,1} distinct => free1 == 0
    #  So the UNIQUE solution: free0=2, free1=0, free2=1.
    #
    # Predicate f(x)=1 iff (val0==2) AND (val1==0) AND (val2==1).
    #   val0==2 : ~b0_0 & b1_0
    #   val1==0 : b0_1 == b1_1
    #   val2==1 : b0_2 & ~b1_2
    #
    # b0_j = problem_qubits[2j], b1_j = problem_qubits[2j+1]

    p = problem_qubits
    b0_0, b1_0 = p[0], p[1]
    b0_1, b1_1 = p[2], p[3]
    b0_2, b1_2 = p[4], p[5]

    a = ancilla_qubits

    # Compute predicate literals into ancillas.
    # cond0 = ~b0_0 & b1_0  -> ancilla a[0]
    qc.x(b0_0)
    qc.ccx(b0_0, b1_0, a[0])
    qc.x(b0_0)

    # cond1 = (b0_1 == b1_1) = ~(b0_1 XOR b1_1) -> ancilla a[1]
    qc.cx(b0_1, a[1])
    qc.cx(b1_1, a[1])
    qc.x(a[1])   # a[1] = 1 iff b0_1 == b1_1

    # cond2 = b0_2 & ~b1_2 -> ancilla a[2]
    qc.x(b1_2)
    qc.ccx(b0_2, b1_2, a[2])
    qc.x(b1_2)

    # AND all three conditions -> ancilla a[3], apply phase, uncompute.
    qc.h(a[3])
    qc.mcx([a[0], a[1], a[2]], a[3])
    qc.h(a[3])

    # Uncompute literals (mirror).
    qc.x(b1_2)
    qc.ccx(b0_2, b1_2, a[2])
    qc.x(b1_2)

    qc.x(a[1])
    qc.cx(b1_1, a[1])
    qc.cx(b0_1, a[1])

    qc.x(b0_0)
    qc.ccx(b0_0, b1_0, a[0])
    qc.x(b0_0)
