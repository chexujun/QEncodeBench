from qiskit import QuantumCircuit
import math

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Text length 5, pattern "110" length 3, offsets 0..2.
    # Pattern position i requires s_(o+i) == pattern[i]; '?' = wildcard.
    pattern = "110"
    n = 5
    L = 3
    offsets = [0, 1, 2]

    # One ancilla per offset holds the AND of the (up to 3) literal conditions.
    # We compute each offset-match into a distinct ancilla, then OR them
    # (via De Morgan) onto the flip using an MCX, then uncompute.
    match_anc = ancilla_qubits[:len(offsets)]  # 3 ancillas
    or_anc = ancilla_qubits[len(offsets)]      # 1 ancilla for phase kickback

    def offset_literals(o):
        # returns list of (qubit, required_bit)
        lits = []
        for i in range(L):
            c = pattern[i]
            if c == '?':
                continue
            lits.append((problem_qubits[o + i], int(c)))
        return lits

    def compute_offset(o, target):
        lits = offset_literals(o)
        controls = []
        for q, bit in lits:
            if bit == 0:
                qc.x(q)
            controls.append(q)
        qc.mcx(controls, target)
        for q, bit in lits:
            if bit == 0:
                qc.x(q)

    # Compute each offset-match ancilla.
    for idx, o in enumerate(offsets):
        compute_offset(o, match_anc[idx])

    # f = OR of match_anc[*].  Use De Morgan:
    # OR = NOT(AND(NOT m_i)).  Flip each match ancilla, MCX into or_anc,
    # so or_anc = 1 iff all flipped == 1, i.e. all m_i == 0 (no match).
    # We want phase -1 when at least one match, i.e. when or_anc == 0.
    for a in match_anc:
        qc.x(a)
    qc.mcx(match_anc, or_anc)
    for a in match_anc:
        qc.x(a)
    # Now or_anc == 1  <=> no match ; or_anc == 0 <=> match.
    # Apply phase -1 when or_anc == 0: X, Z, X.
    qc.x(or_anc)
    qc.z(or_anc)
    qc.x(or_anc)
    # Uncompute or_anc.
    for a in match_anc:
        qc.x(a)
    qc.mcx(match_anc, or_anc)
    for a in match_anc:
        qc.x(a)

    # Uncompute each offset-match ancilla (mirror).
    for idx, o in enumerate(offsets):
        compute_offset(o, match_anc[idx])
