from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    pattern = "1000"
    m = len(pattern)
    n = len(problem_qubits)
    offsets = list(range(n - m + 1))  # 0..4

    # One ancilla per offset holds "match at this offset" (AND of literals).
    off_anc = ancilla_qubits[:len(offsets)]      # 5 ancillas
    or_anc = ancilla_qubits[len(offsets)]        # 1 ancilla for OR / phase

    def compute_offset(o, anc):
        # For each fixed pattern char c at text position o+i:
        #   need s == c. If c=='0', flip that qubit so it reads 1 when s==0.
        # '?' positions are skipped entirely (always match).
        flipped = []
        controls = []
        for i, c in enumerate(pattern):
            if c == '?':
                continue
            q = problem_qubits[o + i]
            if c == '0':
                qc.x(q)
                flipped.append(q)
            controls.append(q)
        if controls:
            qc.mcx(controls, anc)
        else:
            qc.x(anc)
        for q in flipped:
            qc.x(q)  # restore text qubit

    # Compute each offset match into its ancilla.
    for o, anc in zip(offsets, off_anc):
        compute_offset(o, anc)

    # OR of all offset ancillas into or_anc:
    # or_anc = NOT(AND of NOT off_anc)
    for anc in off_anc:
        qc.x(anc)
    qc.mcx(off_anc, or_anc)
    qc.x(or_anc)
    for anc in off_anc:
        qc.x(anc)

    # Phase: -1 iff or_anc == 1.
    qc.z(or_anc)

    # Uncompute OR.
    for anc in off_anc:
        qc.x(anc)
    qc.x(or_anc)
    qc.mcx(off_anc, or_anc)
    for anc in off_anc:
        qc.x(anc)

    # Uncompute each offset ancilla (mirror).
    for o, anc in zip(offsets, off_anc):
        compute_offset(o, anc)
