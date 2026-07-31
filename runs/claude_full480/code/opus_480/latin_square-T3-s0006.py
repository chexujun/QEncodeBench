from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    import math

    # Free cells in order j=0..3: (0,1),(1,0),(2,0),(2,1)
    # Grid:
    #   row0: 1  c0 2       (c0 = free cell 0 at (0,1))
    #   row1: c1 2  1       (c1 = free cell 1 at (1,0))
    #   row2: c2 c3 0       (c2 = free cell 2 at (2,0), c3 = free cell 3 at (2,1))
    #
    # Decoding surjective: 00->0, 01->1, 10->2, 11->0.
    # Value of a free cell as an integer in {0,1,2}:
    #   v(00)=0, v(01)=1, v(10)=2, v(11)=0.
    #
    # Latin square constraints (each row and column has {0,1,2}):
    #  row0: {1, c0, 2} distinct  => c0 = 0
    #  row1: {c1, 2, 1} distinct  => c1 = 0
    #  row2: {c2, c3, 0} distinct => c2,c3 in {1,2} and c2 != c3
    #  col0: {1, c1, c2} distinct => c1=0 given, c2=2  (col0 = {1,c1,c2}=set{0,1,2} => c1=0,c2=2)
    #  col1: {c0, 2, c3} distinct => c0=0 given, c3=1  (col1 = {c0,2,c3}=set{0,1,2} => c0=0,c3=1)
    #  col2: {2,1,0} ok.
    #
    # Unique solution: c0=0, c1=0, c2=2, c3=1.
    # Codes decoding to those values:
    #   c0 value 0 : codes 00 or 11  -> (b0,b1) in {(0,0),(1,1)}  i.e. b0==b1
    #   c1 value 0 : b0==b1
    #   c2 value 2 : code 10 only    -> b0==0, b1==1
    #   c3 value 1 : code 01 only    -> b0==1, b1==0

    def qb(j, bit):
        return problem_qubits[2 * j + bit]

    anc = list(ancilla_qubits)
    # We'll compute per-cell match flags into ancillas a0..a3, AND them into a4,
    # phase, then uncompute.
    a0, a1, a2, a3, a4 = anc[0], anc[1], anc[2], anc[3], anc[4]

    # Cell 0: b0==b1  (flag = NOT(b0 XOR b1))
    # compute XOR into a0 then flip
    qc.cx(qb(0, 0), a0)
    qc.cx(qb(0, 1), a0)
    qc.x(a0)  # a0 = 1 iff b0==b1

    # Cell 1: b0==b1
    qc.cx(qb(1, 0), a1)
    qc.cx(qb(1, 1), a1)
    qc.x(a1)

    # Cell 2: b0==0 and b1==1  -> flag = (NOT b0) AND b1
    qc.x(qb(2, 0))
    qc.ccx(qb(2, 0), qb(2, 1), a2)
    qc.x(qb(2, 0))

    # Cell 3: b0==1 and b1==0 -> flag = b0 AND (NOT b1)
    qc.x(qb(3, 1))
    qc.ccx(qb(3, 0), qb(3, 1), a3)
    qc.x(qb(3, 1))

    # AND all four flags into a4
    qc.mcx([a0, a1, a2, a3], a4)

    # phase
    qc.z(a4)

    # uncompute
    qc.mcx([a0, a1, a2, a3], a4)

    qc.x(qb(3, 1))
    qc.ccx(qb(3, 0), qb(3, 1), a3)
    qc.x(qb(3, 1))

    qc.x(qb(2, 0))
    qc.ccx(qb(2, 0), qb(2, 1), a2)
    qc.x(qb(2, 0))

    qc.x(a1)
    qc.cx(qb(1, 1), a1)
    qc.cx(qb(1, 0), a1)

    qc.x(a0)
    qc.cx(qb(0, 1), a0)
    qc.cx(qb(0, 0), a0)
