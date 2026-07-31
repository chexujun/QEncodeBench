from qiskit import QuantumCircuit
import math


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Free cells (row,col): j0=(0,1), j1=(1,1), j2=(1,2), j3=(2,0)
    # Given grid:
    #   1 . 2
    #   2 . .
    #   . 2 1
    # Decoding: 00->0, 01->1, 10->2, 11->0 (surjective).
    # Each free cell code c=b0+2*b1 must decode to a "value indicator".
    # We track, per cell, a one-hot of decoded value using the two bits,
    # but simpler: compute equality predicates directly on codes.
    #
    # Decoded value v(c): c=0->0, c=1->1, c=2->2, c=3->0.
    # So value==0  iff (b1,b0) in {00,11}  = (b0==b1)
    #    value==1  iff (b1,b0)==01         = (b0 & ~b1)
    #    value==2  iff (b1,b0)==10         = (~b0 & b1)
    #
    # Constraints (rows and cols must be permutations of {0,1,2}).
    # Givens:
    #  row0: cells (0,0)=1, (0,2)=2, free (0,1)=j0  -> j0 must be 0
    #  row1: (1,0)=2, free (1,1)=j1, (1,2)=j2       -> {j1,j2} = {0,1}
    #  row2: free (2,0)=j3, (2,1)=2, (2,2)=1        -> j3 must be 0
    #  col0: (0,0)=1, (1,0)=2, free (2,0)=j3        -> j3 must be 0
    #  col1: free (0,1)=j0, free (1,1)=j1, (2,1)=2  -> {j0,j1}={0,1}
    #  col2: (0,2)=2, free (1,2)=j2, (2,2)=1        -> j2 must be 0
    #
    # Combine: j0=0, j3=0, j2=0, and row1 {j1,j2}={0,1} with j2=0 => j1=1;
    # col1 {j0,j1}={0,1} with j0=0 => j1=1. Consistent.
    # Unique solution: j0=0, j1=1, j2=0, j3=0.
    #
    # Predicate f = [v(j0)==0] & [v(j1)==1] & [v(j2)==0] & [v(j3)==0].

    def b0(j):
        return problem_qubits[2 * j]

    def b1(j):
        return problem_qubits[2 * j + 1]

    # Ancillas: one per cell predicate (4), plus 1 for combined, 1 spare.
    a0 = ancilla_qubits[0]  # v(j0)==0
    a1 = ancilla_qubits[1]  # v(j1)==1
    a2 = ancilla_qubits[2]  # v(j2)==0
    a3 = ancilla_qubits[3]  # v(j3)==0
    combined = ancilla_qubits[4]

    def compute_val0(j, anc):
        # value==0 iff b0==b1 iff not(b0 xor b1); compute xor into anc then flip
        qc.cx(b0(j), anc)
        qc.cx(b1(j), anc)
        qc.x(anc)  # anc = 1 iff b0==b1

    def uncompute_val0(j, anc):
        qc.x(anc)
        qc.cx(b1(j), anc)
        qc.cx(b0(j), anc)

    def compute_val1(j, anc):
        # value==1 iff b0 & ~b1
        qc.x(b1(j))
        qc.ccx(b0(j), b1(j), anc)
        qc.x(b1(j))

    def uncompute_val1(j, anc):
        qc.x(b1(j))
        qc.ccx(b0(j), b1(j), anc)
        qc.x(b1(j))

    # Compute predicates
    compute_val0(0, a0)
    compute_val1(1, a1)
    compute_val0(2, a2)
    compute_val0(3, a3)

    # combined = AND of a0,a1,a2,a3
    qc.mcx([a0, a1, a2, a3], combined)

    # phase
    qc.z(combined)

    # uncompute combined
    qc.mcx([a0, a1, a2, a3], combined)

    # uncompute predicates (mirror)
    uncompute_val0(3, a3)
    uncompute_val0(2, a2)
    uncompute_val1(1, a1)
    uncompute_val0(0, a0)
