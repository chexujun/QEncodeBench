from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    p = problem_qubits
    a = ancilla_qubits

    # Clauses as lists of (variable_index, is_negated) literals.
    # A clause is satisfied unless ALL its literals are false.
    # Literal (i, neg): false when x_i == (1 if neg else 0).
    clauses = [
        [(0, True), (1, True), (2, True)],    # NOT x0 OR NOT x1 OR NOT x2
        [(0, True), (1, False), (2, True)],   # NOT x0 OR x1 OR NOT x2
        [(0, False), (1, False), (4, True)],  # x0 OR x1 OR NOT x4
        [(0, True), (2, False), (3, True)],   # NOT x0 OR x2 OR NOT x3
    ]

    def compute_clauses():
        for k, clause in enumerate(clauses):
            anc = a[k]
            # For each literal, X the qubit so that "false-literal" maps to |1>.
            # Literal is false when x_i == (1 if neg else 0).
            # We want controls = 1 when literal is false.
            # If neg (literal = NOT x_i): false when x_i == 1 -> control already 1, no X.
            # If not neg (literal = x_i): false when x_i == 0 -> apply X to make control 1.
            for (i, neg) in clause:
                if not neg:
                    qc.x(p[i])
            controls = [p[i] for (i, _) in clause]
            # anc becomes 1 iff all literals false (clause unsatisfied).
            qc.mcx(controls, anc)
            for (i, neg) in clause:
                if not neg:
                    qc.x(p[i])
        # Now anc[k] == 1 iff clause k is UNSATISFIED.
        # Flip so anc[k] == 1 iff clause k is SATISFIED.
        for k in range(len(clauses)):
            qc.x(a[k])

    compute_clauses()
    # Phase -1 iff all clauses satisfied: all anc[0..3] == 1.
    qc.h(a[4])
    qc.mcx([a[0], a[1], a[2], a[3]], a[4])
    qc.h(a[4])
    # Uncompute.
    for k in range(len(clauses)):
        qc.x(a[k])
    for k in reversed(range(len(clauses))):
        clause = clauses[k]
        anc = a[k]
        for (i, neg) in clause:
            if not neg:
                qc.x(p[i])
        controls = [p[i] for (i, _) in clause]
        qc.mcx(controls, anc)
        for (i, neg) in clause:
            if not neg:
                qc.x(p[i])
