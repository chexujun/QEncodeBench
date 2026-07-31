from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    p = problem_qubits
    anc = ancilla_qubits

    # Free cells: j0=(0,0), j1=(1,1), j2=(2,1)
    # code bits: cell j -> low=p[2j], high=p[2j+1]; value = low + 2*high, with 11->0.
    # Decoded value equals code except code 3 (11) -> 0.
    #
    # Grid givens:
    #   row0: . 2 1   -> free (0,0)=v0 ; row0 has {2,1}; col0 has (0,0),(1,0)=1,(2,0)=2
    #   row1: 1 . 2   -> free (1,1)=v1 ; row1 has {1,2}; col1 has (0,1)=2,(1,1)=v1,(2,1)=v2
    #   row2: 2 . 0   -> free (2,1)=v2 ; row2 has {2,0}; col1 free cells v1,v2
    #
    # Constraints forcing uniqueness:
    #   v0: row0 needs the missing value 0; col0 already {1,2} -> needs 0. So v0 must = 0.
    #   v1: row1 needs missing value 0; col1 must have {0,1,2}: col1 = {2, v1, v2}. -> v1 must = 0.
    #   v2: row2 needs missing value 1; -> v2 must = 1.
    #   Check col1: {2, v1=0, v2=1} = {0,1,2}. Valid. Rows all valid.
    #
    # So f(x)=1 iff v0==0 AND v1==0 AND v2==1.
    #
    # value(cell j): with bits low,high:
    #   v==0  iff code in {00, 11} iff low==high  (00 or 11)
    #   v==1  iff code==01 iff low==1,high==0
    #
    # Define per-cell predicate flags into ancillas, all returning to |0>.

    # Cell0: v0==0  <=>  low0 == high0  (low0 XNOR high0 == 1)
    l0, h0 = p[0], p[1]
    # Cell1: v1==0  <=>  low1 == high1
    l1, h1 = p[2], p[3]
    # Cell2: v2==1  <=>  low2==1 and high2==0
    l2, h2 = p[4], p[5]

    a0, a1, a2 = anc[0], anc[1], anc[2]

    # --- compute a0 = (l0 XNOR h0) ---
    qc.cx(l0, a0)
    qc.cx(h0, a0)
    qc.x(a0)            # a0 = NOT(l0 XOR h0) = (l0==h0)

    # --- compute a1 = (l1 XNOR h1) ---
    qc.cx(l1, a1)
    qc.cx(h1, a1)
    qc.x(a1)

    # --- compute a2 = (l2==1 AND h2==0) ---
    qc.x(h2)           # flip so condition becomes l2==1 AND h2'==1
    qc.ccx(l2, h2, a2)
    qc.x(h2)           # restore h2

    # --- phase: -1 iff a0 AND a1 AND a2 ---
    qc.h(a2)
    qc.ccx(a0, a1, a2)
    qc.h(a2)

    # --- uncompute a2 ---
    qc.x(h2)
    qc.ccx(l2, h2, a2)
    qc.x(h2)

    # --- uncompute a1 ---
    qc.x(a1)
    qc.cx(h1, a1)
    qc.cx(l1, a1)

    # --- uncompute a0 ---
    qc.x(a0)
    qc.cx(h0, a0)
    qc.cx(l0, a0)
