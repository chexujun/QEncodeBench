from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Free cells (row,col): j0=(0,0), j1=(0,1), j2=(0,2), j3=(2,0)
    # Codes: cell j uses b0=problem_qubits[2j], b1=problem_qubits[2j+1]
    # Decode: 00->0, 01->1, 10->2, 11->0
    # Grid givens:
    #   row0: free f0 f1 f2
    #   row1: 1 0 2
    #   row2: f3 2 1
    # Columns:
    #   col0: f0, 1, f3
    #   col1: f1, 0, 2
    #   col2: f2, 2, 1

    # value-equality helper: for cell j and target value v in {0,1,2}, produce
    # a predicate qubit that is 1 iff decoded value == v.
    # decode value:
    #   v0 (value 0): code 00 or 11  => (b0 == b1)  -> b0 XNOR b1
    #   v1 (value 1): code 01        => b0 & ~b1
    #   v2 (value 2): code 10        => ~b0 & b1

    cells = [(problem_qubits[2*j], problem_qubits[2*j+1]) for j in range(4)]

    # We need f(x)=1 iff the completed grid is a valid Latin square.
    # Determine constraints. Solve structurally: known cells fix values.
    # row0 must be a permutation of {0,1,2}: f0,f1,f2 distinct and each in {0,1,2}(always).
    # row2: f3,2,1 -> f3 must be 0.
    # col0: f0,1,f3 -> with f3=0: f0 must be 2.
    # col1: f1,0,2 -> f1 must be 1.
    # col2: f2,2,1 -> f2 must be 0.
    # Then row0 = f0=2,f1=1,f2=0 -> {2,1,0} valid. Consistent unique solution.
    # So f(x)=1 iff  f0==2 and f1==1 and f2==0 and f3==0.

    # Build predicate literals into ancillas, AND them, phase, uncompute.
    # ancilla_qubits: 6 available. Use a0..a3 for the four equality predicates,
    # a4 as combined AND target for phase.
    a = ancilla_qubits

    def eq0(b0, b1, tgt):
        # value 0 iff b0 == b1 (XNOR): tgt ^= not(b0 xor b1)
        qc.cx(b0, tgt)
        qc.cx(b1, tgt)
        qc.x(tgt)   # now tgt = XNOR
    def eq0_un(b0, b1, tgt):
        qc.x(tgt)
        qc.cx(b1, tgt)
        qc.cx(b0, tgt)
    def eq1(b0, b1, tgt):
        # value 1 iff b0 & ~b1
        qc.x(b1)
        qc.ccx(b0, b1, tgt)
        qc.x(b1)
    def eq1_un(b0, b1, tgt):
        qc.x(b1)
        qc.ccx(b0, b1, tgt)
        qc.x(b1)
    def eq2(b0, b1, tgt):
        # value 2 iff ~b0 & b1
        qc.x(b0)
        qc.ccx(b0, b1, tgt)
        qc.x(b0)
    def eq2_un(b0, b1, tgt):
        qc.x(b0)
        qc.ccx(b0, b1, tgt)
        qc.x(b0)

    b00, b01 = cells[0]  # f0, need ==2
    b10, b11 = cells[1]  # f1, need ==1
    b20, b21 = cells[2]  # f2, need ==0
    b30, b31 = cells[3]  # f3, need ==0

    # compute predicates
    eq2(b00, b01, a[0])
    eq1(b10, b11, a[1])
    eq0(b20, b21, a[2])
    eq0(b30, b31, a[3])

    # phase -1 iff all four are 1
    qc.h(a[4])
    qc.mcx([a[0], a[1], a[2], a[3]], a[4])
    qc.h(a[4])

    # uncompute predicates (mirror)
    eq0_un(b30, b31, a[3])
    eq0_un(b20, b21, a[2])
    eq1_un(b10, b11, a[1])
    eq2_un(b00, b01, a[0])
