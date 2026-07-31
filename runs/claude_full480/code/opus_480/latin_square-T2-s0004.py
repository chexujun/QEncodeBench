import math
from qiskit import QuantumCircuit


def build_oracle(qc, problem_qubits, ancilla_qubits):
    # Free cells (row,col): j0=(1,1), j1=(2,1), j2=(2,2)
    # Grid givens:
    #   row0: 2 1 0
    #   row1: 1 . 2   -> (1,1)=j0 free; row1 has {1,2} given
    #   row2: 0 . .   -> (2,1)=j1, (2,2)=j2 free; row2 has {0} given
    # cols:
    #   col0: 2,1,0 (full, valid)
    #   col1: 1,.,. -> given {1}; free j0(row1),j1(row2)
    #   col2: 0,2,. -> given {0,2}; free j2(row2)
    #
    # Decoding surjective: 00->0,01->1,10->2,11->0. value2(cell)=1 iff code==10.
    # Let for cell j: bits b0=problem_qubits[2j], b1=problem_qubits[2j+1].
    # value indicator via decode: v0 = (b1==0 and any b0) OR code11 -> value0 iff (b0,b1) in {00,11} => b0==b1
    #   value0: b0==b1
    #   value1: b0=1,b1=0
    #   value2: b0=0,b1=1
    #
    # Constraints for validity:
    # Row1: {1(given),2(given), j0}. j0 must be 0. (since row needs 0,1,2)
    #   -> j0 == value0  -> b0_0 == b1_0.
    # Row2: {0(given), j1, j2} must be {1,2} in some order (need 1 and 2).
    # Col1: {1(given), j0(row1), j1(row2)}. j0 must be 0 (from row1). Need col to be {0,1,2}: has 1 given, j0=0, so j1 must be 2.
    #   -> j1 == value2.
    # Col2: {0(given),2(given), j2(row2)}. j2 must be 1 -> value1.
    # Row2 check: j1=2, j2=1, given 0 -> {0,1,2} valid. consistent.
    #
    # So f=1 iff:
    #   j0 value0: b0_0 == b1_0
    #   j1 value2: b0_1==0 and b1_1==1
    #   j2 value1: b0_2==1 and b1_2==0

    p = problem_qubits
    b0_0, b1_0 = p[0], p[1]
    b0_1, b1_1 = p[2], p[3]
    b0_2, b1_2 = p[4], p[5]

    a = ancilla_qubits
    # a0: j0 satisfied = (b0_0 == b1_0) = NOT(b0_0 XOR b1_0)
    # a1: j1 satisfied = (b0_1==0)&(b1_1==1)
    # a2: j2 satisfied = (b0_2==1)&(b1_2==0)
    # final flag = a0 & a1 & a2

    # compute a0 = b0_0 XNOR b1_0
    qc.cx(b0_0, a[0])
    qc.cx(b1_0, a[0])
    qc.x(a[0])  # now a0 = 1 iff equal

    # compute a1 = (NOT b0_1) & b1_1
    qc.x(b0_1)
    qc.ccx(b0_1, b1_1, a[1])
    qc.x(b0_1)

    # compute a2 = b0_2 & (NOT b1_2)
    qc.x(b1_2)
    qc.ccx(b0_2, b1_2, a[2])
    qc.x(b1_2)

    # flag = a0 & a1 & a2
    qc.ccx(a[0], a[1], a[3])
    qc.ccx(a[3], a[2], a[4])

    # phase
    qc.z(a[4])

    # uncompute
    qc.ccx(a[3], a[2], a[4])
    qc.ccx(a[0], a[1], a[3])

    qc.x(b1_2)
    qc.ccx(b0_2, b1_2, a[2])
    qc.x(b1_2)

    qc.x(b0_1)
    qc.ccx(b0_1, b1_1, a[1])
    qc.x(b0_1)

    qc.x(a[0])
    qc.cx(b1_0, a[0])
    qc.cx(b0_0, a[0])
