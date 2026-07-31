from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    pattern = "11?01"
    n_text = 7
    L = len(pattern)
    offsets = list(range(n_text - L + 1))  # 0,1,2

    match_ancillas = ancilla_qubits[:len(offsets)]  # one per offset
    or_ancilla = ancilla_qubits[len(offsets)]       # final OR/phase target

    def compute_match(offset, target):
        # For each fixed pattern bit, X the text qubit if pattern bit is 0,
        # so that an all-ones MCX detects the match.
        fixed = []
        for i, ch in enumerate(pattern):
            if ch == '?':
                continue
            q = problem_qubits[offset + i]
            fixed.append((q, ch))
        for q, ch in fixed:
            if ch == '0':
                qc.x(q)
        ctrls = [q for q, _ in fixed]
        qc.mcx(ctrls, target)
        for q, ch in fixed:
            if ch == '0':
                qc.x(q)

    # Compute each offset's match indicator into its own ancilla.
    for off, anc in zip(offsets, match_ancillas):
        compute_match(off, anc)

    # OR of match ancillas into or_ancilla:
    # or = NOT( AND(NOT m_j) ). Flip all m_j, MCX into or (=1 iff all flipped=1
    # i.e. all m_j=0 -> or=1 meaning no match), then X or to invert.
    for anc in match_ancillas:
        qc.x(anc)
    qc.mcx(match_ancillas, or_ancilla)
    for anc in match_ancillas:
        qc.x(anc)
    qc.x(or_ancilla)  # or_ancilla = OR of matches

    # Phase flip iff at least one match.
    qc.z(or_ancilla)

    # Uncompute OR.
    qc.x(or_ancilla)
    for anc in match_ancillas:
        qc.x(anc)
    qc.mcx(match_ancillas, or_ancilla)
    for anc in match_ancillas:
        qc.x(anc)

    # Uncompute each match indicator (mirror).
    for off, anc in zip(offsets, match_ancillas):
        compute_match(off, anc)
