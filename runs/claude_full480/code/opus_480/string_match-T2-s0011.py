from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # pattern = "101?" over positions i=0..3; wildcard at i=3.
    # Fixed comparisons: p0=1, p1=0, p2=1 ; p3 is '?' (ignored).
    # Text length 6, offsets o in 0..2. Match at offset o means:
    #   s[o+0]==1 and s[o+1]==0 and s[o+2]==1  (position 3 wildcard: no constraint)
    # f(x) = OR over o in {0,1,2} of match(o).
    #
    # Strategy: for each offset compute a per-offset "match" flag into an ancilla.
    # match(o) = s[o] AND (NOT s[o+1]) AND s[o+2].
    # Use 3 ancillas (one per offset) as match flags, OR them via a marking
    # ancilla with phase, then uncompute.

    a0, a1, a2, m = ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[2], ancilla_qubits[3]
    offsets = [0, 1, 2]
    match_anc = [a0, a1, a2]

    def compute_match(o, anc):
        p0 = problem_qubits[o + 0]
        p1 = problem_qubits[o + 1]
        p2 = problem_qubits[o + 2]
        # need p0=1, p1=0, p2=1 -> flip p1 so all three controls active on 1
        qc.x(p1)
        qc.ccx(p0, p1, anc)      # temporarily anc = p0 AND (NOT p1)
        # AND with p2: use anc as intermediate. We want anc = p0 & ~p1 & p2.
        # Do it in two steps needs a temp; instead directly mcx with 3 controls
        # Undo the partial ccx and redo with 3-control mcx.
        qc.ccx(p0, p1, anc)      # uncompute the partial
        qc.mcx([p0, p1, p2], anc)
        qc.x(p1)

    # compute all match flags
    for o, anc in zip(offsets, match_anc):
        compute_match(o, anc)

    # OR of the three flags: m = a0 OR a1 OR a2.
    # Use De Morgan: NOT m computed as AND of NOTs, then flip.
    qc.x(a0); qc.x(a1); qc.x(a2)
    qc.mcx([a0, a1, a2], m)      # m = (NOT a0)(NOT a1)(NOT a2) = NOT(OR)
    qc.x(a0); qc.x(a1); qc.x(a2)
    qc.x(m)                      # m = OR of flags

    # phase
    qc.z(m)

    # uncompute m
    qc.x(m)
    qc.x(a0); qc.x(a1); qc.x(a2)
    qc.mcx([a0, a1, a2], m)
    qc.x(a0); qc.x(a1); qc.x(a2)

    # uncompute match flags (mirror)
    for o, anc in reversed(list(zip(offsets, match_anc))):
        compute_match(o, anc)
