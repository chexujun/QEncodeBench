from qiskit import QuantumCircuit
import math


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Free cells (row,col): 0:(0,1) 1:(0,2) 2:(1,2) 3:(2,2)
    # Grid givens:
    #  row0: 1 . .    -> (0,0)=1
    #  row1: 2 1 .    -> (1,0)=2 (1,1)=1
    #  row2: 0 2 .    -> (2,0)=0 (2,1)=2
    # Free cell value = decode(code): 00->0,01->1,10->2,11->0
    # So value==0 iff code in {00,11} i.e. b0==b1
    #    value==1 iff code==01 i.e. b0=1,b1=0
    #    value==2 iff code==10 i.e. b0=0,b1=1
    def bits(j):
        return problem_qubits[2 * j], problem_qubits[2 * j + 1]

    # For a free cell, build a 2-wire "one-hot"-ish predicate for each value.
    # We need equality/inequality constraints. We'll express constraints as
    # products of literals over the b0,b1 of each free cell, and compute the
    # full predicate f = AND of all constraints into one ancilla, phase, uncompute.
    #
    # Constraints for a valid Latin square:
    # Cells and their values:
    #   c0 = free0 at (0,1)
    #   c1 = free1 at (0,2)
    #   c2 = free2 at (1,2)
    #   c3 = free3 at (2,2)
    #
    # Row0: {given 1, c0, c1} = {0,1,2}
    # Row1: {given 2, given 1, c2} = {0,1,2} -> c2 must be 0
    # Row2: {given 0, given 2, c3} = {0,1,2} -> c3 must be 1
    # Col0: given {1,2,0} ok (no free)
    # Col1: {given .? } col1 values: (0,1)=c0,(1,1)=1,(2,1)=2 = {0,1,2} -> c0 must be 0
    # Col2: {(0,2)=c1,(1,2)=c2,(2,2)=c3} = {0,1,2}
    #
    # From c2=0 (row1), c3=1 (row2), c0=0 (col1).
    # Row0 {1,c0,c1}: c0=0 -> need c1=2.
    # Col2 {c1,c2,c3}={c1,0,1} -> need c1=2. consistent.
    # So unique solution: c0=0, c1=2, c2=0, c3=1.
    #
    # value==0 : b0==b1 (states 00 or 11)
    # value==2 : b0=0,b1=1
    # value==1 : b0=1,b1=0
    #
    # Build predicate literals into ancillas.
    b0_0, b1_0 = bits(0)
    b0_1, b1_1 = bits(1)
    b0_2, b1_2 = bits(2)
    b0_3, b1_3 = bits(3)

    a = ancilla_qubits  # 6 ancillas
    t0, t1, t2, t3, tf = a[0], a[1], a[2], a[3], a[4]

    # ---- compute per-cell predicate bits ----
    # t0 = (c0 == 0) = (b0_0 == b1_0) = NOT(b0_0 XOR b1_0)
    qc.cx(b0_0, t0)
    qc.cx(b1_0, t0)
    qc.x(t0)  # t0 = 1 iff b0_0==b1_0

    # t1 = (c1 == 2) = (b0_1==0 and b1_1==1)
    qc.x(b0_1)
    qc.ccx(b0_1, b1_1, t1)
    qc.x(b0_1)

    # t2 = (c2 == 0) = (b0_2 == b1_2)
    qc.cx(b0_2, t2)
    qc.cx(b1_2, t2)
    qc.x(t2)

    # t3 = (c3 == 1) = (b0_3==1 and b1_3==0)
    qc.x(b1_3)
    qc.ccx(b0_3, b1_3, t3)
    qc.x(b1_3)

    # ---- combine: tf = t0 AND t1 AND t2 AND t3 ----
    qc.mcx([t0, t1, t2, t3], tf)

    # ---- phase ----
    qc.z(tf)

    # ---- uncompute ----
    qc.mcx([t0, t1, t2, t3], tf)

    qc.x(b1_3)
    qc.ccx(b0_3, b1_3, t3)
    qc.x(b1_3)

    qc.cx(b0_2, t2)
    qc.cx(b1_2, t2)
    qc.x(t2)

    qc.x(b0_1)
    qc.ccx(b0_1, b1_1, t1)
    qc.x(b0_1)

    qc.cx(b0_0, t0)
    qc.cx(b1_0, t0)
    qc.x(t0)
