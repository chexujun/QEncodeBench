from qiskit import QuantumCircuit
import math

def build_oracle(qc: QuantumCircuit, problem_qubits, ancilla_qubits):
    # Free cells in order: (0,2),(2,0),(2,1),(2,2)
    # Each free cell j: low bit = problem_qubits[2j], high bit = problem_qubits[2j+1]
    # Decode: 00->0, 01->1, 10->2, 11->0  (surjective, code 11 == value 0)
    #
    # Grid:
    #   row0: 1 2 A        (A = cell0 at (0,2))
    #   row1: 0 1 2
    #   row2: B C D        (B=cell1 (2,0), C=cell2 (2,1), D=cell3 (2,2))
    #
    # Constraints for a valid Latin square (values 0,1,2 once per row/col):
    #  Row0: {1,2,A} distinct => A must be 0.
    #  Col2: {A,2,D} distinct, col1: {2,1,C}=>C must be 0, col0:{1,0,B}=>B must be 2.
    #  Row2: {B,C,D} distinct.
    # Solve deterministically:
    #  A=0 (row0 needs 0). Col2 has A=0,2, so D must be 1.
    #  Col1 has 2,1 => C=0. Col0 has 1,0 => B=2.
    #  Row2 = {B=2,C=0,D=1} => {2,0,1} distinct. Valid.
    # Unique solution: A=0(00), B=2(10), C=0(00), D=1(01).
    #
    # But decoding is surjective: value 0 <- code 00 OR 11; value 2 <- code 10 only;
    # value 1 <- code 01 only.
    # So required per-cell value sets translate to accepted codes:
    #  A value 0 -> codes {00, 11}
    #  B value 2 -> code {10}
    #  C value 0 -> codes {00, 11}
    #  D value 1 -> code {01}

    # helper: build predicate qA0 = (cellA is value 0) into ancilla, etc.
    # We'll compute individual per-cell "matches required value" flags then AND them.

    p = problem_qubits
    anc = ancilla_qubits

    # bit layout per cell j: b0=p[2j] (low), b1=p[2j+1] (high)
    # value(code): 0 <-> (b0,b1) in {(0,0),(1,1)}  i.e. b0==b1
    #              1 <-> (1,0)  b0=1,b1=0
    #              2 <-> (0,1)  b0=0,b1=1
    # Note code c=b0+2*b1: 00->0(v0),01(b0=1,b1=0)->? c=1 value1; 10 means b0=0,b1=1 c=2 value2; 11 value0.
    # So: value0 <=> b0==b1 ; value1 <=> b0=1,b1=0 ; value2 <=> b0=0,b1=1.

    def cell_bits(j):
        return p[2*j], p[2*j+1]  # b0, b1

    # Flags into ancillas: use anc[0..3] for the 4 cell predicates, anc[4] optional.
    # Cell A (j=0): value 0 <=> b0==b1. Flag = XNOR(b0,b1).
    b0, b1 = cell_bits(0)
    fA = anc[0]
    # XNOR: fA = 1 iff b0==b1. Compute: fA starts 0; cx b0->fA; cx b1->fA gives XOR; then X to get XNOR.
    qc.cx(b0, fA)
    qc.cx(b1, fA)
    qc.x(fA)  # now fA = NOT(b0 xor b1) = (b0==b1) = value0

    # Cell C (j=2): value 0 <=> b0==b1.
    b0c, b1c = cell_bits(2)
    fC = anc[1]
    qc.cx(b0c, fC)
    qc.cx(b1c, fC)
    qc.x(fC)

    # Cell B (j=1): value 2 <=> b0=0, b1=1.  Flag = (NOT b0) AND b1.
    b0b, b1b = cell_bits(1)
    fB = anc[2]
    qc.x(b0b)              # b0'=NOT b0
    qc.ccx(b0b, b1b, fB)  # fB = (NOT b0) AND b1
    qc.x(b0b)             # restore

    # Cell D (j=3): value 1 <=> b0=1, b1=0.  Flag = b0 AND (NOT b1).
    b0d, b1d = cell_bits(3)
    fD = anc[3]
    qc.x(b1d)
    qc.ccx(b0d, b1d, fD)
    qc.x(b1d)

    # Now AND all four flags into anc[4], phase, uncompute.
    fAll = anc[4]
    qc.mcx([fA, fB, fC, fD], fAll)
    qc.z(fAll)
    qc.mcx([fA, fB, fC, fD], fAll)

    # Uncompute per-cell flags (mirror).
    # Cell D
    qc.x(b1d)
    qc.ccx(b0d, b1d, fD)
    qc.x(b1d)
    # Cell B
    qc.x(b0b)
    qc.ccx(b0b, b1b, fB)
    qc.x(b0b)
    # Cell C
    qc.x(fC)
    qc.cx(b1c, fC)
    qc.cx(b0c, fC)
    # Cell A
    qc.x(fA)
    qc.cx(b1, fA)
    qc.cx(b0, fA)
