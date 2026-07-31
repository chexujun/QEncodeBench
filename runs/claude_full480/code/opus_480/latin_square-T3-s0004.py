from qiskit import QuantumCircuit
import numpy as np


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Free cells in order: (0,0),(0,1),(2,0),(2,1)
    # Grid givens:
    #   row0: (0,0)=A, (0,1)=B, (0,2)=2
    #   row1: 1,2,0
    #   row2: (2,0)=C, (2,1)=D, (2,2)=1
    # cells A,B,C,D correspond to free j=0,1,2,3
    # value(cell) via code c=b0+2*b1, with 11->0.
    # decoded value v in {0,1,2}: v0 = (code==1), v1=(code==2), else 0.
    # We need one-hot value indicators eq0,eq1,eq2 per cell.

    def cell_qubits(j):
        return problem_qubits[2 * j], problem_qubits[2 * j + 1]

    # helper: build indicator "cell j decodes to value val" into ancilla anc.
    # code: b0,b1. decode: val0 <-> code00 or code11 ; val1<->01 ; val2<->10
    # eqval indicator:
    #   val0: (b0==b1)          -> 1 when 00 or 11
    #   val1: (b0==1 and b1==0)
    #   val2: (b0==0 and b1==1)
    def compute_eq(j, val, anc):
        b0, b1 = cell_qubits(j)
        if val == 0:
            # b0==b1  -> not(b0 xor b1); compute xor into anc then flip
            qc.cx(b0, anc)
            qc.cx(b1, anc)
            qc.x(anc)
        elif val == 1:
            # b0 & ~b1
            qc.x(b1)
            qc.ccx(b0, b1, anc)
            qc.x(b1)
        elif val == 2:
            # ~b0 & b1
            qc.x(b0)
            qc.ccx(b0, b1, anc)
            qc.x(b0)

    def uncompute_eq(j, val, anc):
        b0, b1 = cell_qubits(j)
        if val == 0:
            qc.x(anc)
            qc.cx(b1, anc)
            qc.cx(b0, anc)
        elif val == 1:
            qc.x(b1)
            qc.ccx(b0, b1, anc)
            qc.x(b1)
        elif val == 2:
            qc.x(b0)
            qc.ccx(b0, b1, anc)
            qc.x(b0)

    # Constraints for a valid Latin square given fixed cells.
    # Grid:
    #  A B 2
    #  1 2 0
    #  C D 1
    # Row0: {A,B,2} all diff -> A!=2, B!=2, A!=B
    # Row2: {C,D,1} all diff -> C!=1, D!=1, C!=D
    # Col0: {A,1,C} all diff -> A!=1, C!=1, A!=C
    # Col1: {B,2,D} all diff -> B!=2, D!=2, B!=D
    # (rows 1 already valid; col2 fixed 2,0,1 valid)
    # Combined per-cell forced values:
    #   A != 2, A != 1 -> A == 0
    #   B != 2 -> B in {0,1}
    #   C != 1 -> C in {0,2}
    #   D != 1, D != 2 -> D == 0
    # A==0 and C!=A -> C!=0 -> C==2
    # D==0 and B!=D -> B!=0 -> B==1
    # So unique solution: A=0,B=1,C=2,D=0.
    # Predicate f=1 iff (A==0)&(B==1)&(C==2)&(D==0).

    e0 = ancilla_qubits[0]  # A==0
    e1 = ancilla_qubits[1]  # B==1
    e2 = ancilla_qubits[2]  # C==2
    e3 = ancilla_qubits[3]  # D==0
    phase_anc = ancilla_qubits[4]

    compute_eq(0, 0, e0)
    compute_eq(1, 1, e1)
    compute_eq(2, 2, e2)
    compute_eq(3, 0, e3)

    # AND of e0..e3 into phase via mcx then z then uncompute (or mcp)
    qc.mcx([e0, e1, e2, e3], phase_anc)
    qc.z(phase_anc)
    qc.mcx([e0, e1, e2, e3], phase_anc)

    uncompute_eq(3, 0, e3)
    uncompute_eq(2, 2, e2)
    uncompute_eq(1, 1, e1)
    uncompute_eq(0, 0, e0)
