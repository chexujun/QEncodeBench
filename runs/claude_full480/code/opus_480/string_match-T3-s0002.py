from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    pattern = "0011"
    n = len(problem_qubits)
    m = len(pattern)
    offsets = list(range(n - m + 1))  # 0..4

    # Fixed pattern positions (non-wildcard) per offset
    fixed = []  # list of (offset, [(text_index, required_bit), ...])
    for o in offsets:
        constraints = []
        for i, ch in enumerate(pattern):
            if ch == '?':
                continue
            constraints.append((o + i, int(ch)))
        fixed.append((o, constraints))

    off_anc = ancilla_qubits[:len(offsets)]      # one ancilla per offset match flag
    out_anc = ancilla_qubits[len(offsets)]       # OR-accumulator ancilla

    def compute_match(o, constraints, target):
        # Set target = AND over constraints (text bit == required bit).
        # For required bit 0, flip the text qubit so that |0> maps to |1>.
        ctrls = []
        for (idx, bit) in constraints:
            q = problem_qubits[idx]
            if bit == 0:
                qc.x(q)
            ctrls.append(q)
        qc.mcx(ctrls, target)
        # restore flips
        for (idx, bit) in constraints:
            if bit == 0:
                qc.x(problem_qubits[idx])

    # Compute each offset match flag
    for (o, constraints), tgt in zip(fixed, off_anc):
        compute_match(o, constraints, tgt)

    # OR of all offset flags into out_anc:
    # out = NOT(AND of NOT(flags)). Flip all flags, mcx, then flip back.
    for a in off_anc:
        qc.x(a)
    qc.mcx(off_anc, out_anc)
    qc.x(out_anc)
    for a in off_anc:
        qc.x(a)

    # Phase kick on the OR result
    qc.z(out_anc)

    # Uncompute OR
    for a in off_anc:
        qc.x(a)
    qc.x(out_anc)
    qc.mcx(off_anc, out_anc)
    for a in off_anc:
        qc.x(a)

    # Uncompute offset flags (mirror)
    for (o, constraints), tgt in reversed(list(zip(fixed, off_anc))):
        compute_match(o, constraints, tgt)
