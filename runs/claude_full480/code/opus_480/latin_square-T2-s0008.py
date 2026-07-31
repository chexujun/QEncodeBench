from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    import math

    # Free cells (row, col): j=0 -> (1,2), j=1 -> (2,1), j=2 -> (2,2)
    # Givens:
    #  row0: 0 1 2
    #  row1: 1 2 .   -> (1,2) free
    #  row2: 2 . .   -> (2,1),(2,2) free
    #
    # Value decode from code c (b0=problem_qubits[2j], b1=problem_qubits[2j+1]):
    #   00->0, 01->1, 10->2, 11->0
    #
    # Constraints for a valid Latin square:
    #  Row1 has givens {1,2}; free (1,2) must be 0.
    #  Row2 has given {2}; free (2,1),(2,2) must be {0,1} in some order.
    #  Col0 given {0,1,2} full.
    #  Col1 has givens row0=1; free (2,1). Also (2,1) with row1 col1 given=2.
    #        Col1 = {1(row0), 2(row1), (2,1)} -> (2,1) must be 0.
    #  Col2 has givens row0=2; free (1,2),(2,2). row1 col2 = (1,2).
    #        Col2 = {2(row0), (1,2), (2,2)}.
    #
    # Deduce the unique solution:
    #  (1,2)=0 (row1). (2,1)=0 (col1). row2 = {2, (2,1),(2,2)} must be {0,1,2}
    #   -> (2,1),(2,2) = {0,1}. (2,1)=0 => (2,2)=1.
    #  Check col2 = {2,0,1} valid. Good.
    #
    # Unique solution values: (1,2)=0, (2,1)=0, (2,2)=1.
    # In codes: value0 <- code 00 or 11 ; value1 <- code 01.
    #  free0 (1,2) value0: code in {00,11}
    #  free1 (2,1) value0: code in {00,11}
    #  free2 (2,2) value1: code == 01  (only 01 decodes to 1)

    p = problem_qubits
    anc = ancilla_qubits

    # Indicator ancillas for each free cell's required-value predicate.
    a0 = anc[0]  # free0 == value0
    a1 = anc[1]  # free1 == value0
    a2 = anc[2]  # free2 == value1

    b0_0, b1_0 = p[0], p[1]
    b0_1, b1_1 = p[2], p[3]
    b0_2, b1_2 = p[4], p[5]

    # free_j == value0  iff  code in {00,11}  iff  b0 == b1.
    # a = 1 iff b0 == b1 = NOT(b0 XOR b1).
    def eq_value0(bl, bh, a):
        qc.cx(bl, a)
        qc.cx(bh, a)
        qc.x(a)  # a = NOT(b0 xor b1)

    def eq_value0_un(bl, bh, a):
        qc.x(a)
        qc.cx(bh, a)
        qc.cx(bl, a)

    # free2 == value1 iff code==01 iff b0==1 and b1==0.
    # a2 = b0 AND (NOT b1)
    def eq_value1_01(bl, bh, a):
        qc.x(bh)
        qc.ccx(bl, bh, a)
        qc.x(bh)

    def eq_value1_01_un(bl, bh, a):
        qc.x(bh)
        qc.ccx(bl, bh, a)
        qc.x(bh)

    # Compute
    eq_value0(b0_0, b1_0, a0)
    eq_value0(b0_1, b1_1, a1)
    eq_value1_01(b0_2, b1_2, a2)

    # Phase: -1 iff a0 AND a1 AND a2
    qc.h(anc[3])
    qc.x(anc[3])
    qc.mcx([a0, a1, a2], anc[3])
    qc.x(anc[3])
    qc.h(anc[3])

    # Uncompute
    eq_value1_01_un(b0_2, b1_2, a2)
    eq_value0_un(b0_1, b1_1, a1)
    eq_value0_un(b0_0, b1_0, a0)
