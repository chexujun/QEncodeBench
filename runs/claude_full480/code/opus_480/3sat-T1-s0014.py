from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    x0, x1, x2 = problem_qubits[0], problem_qubits[1], problem_qubits[2]
    c = [ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[2], ancilla_qubits[3]]
    out = ancilla_qubits[4]

    # Clause literals: for each clause, list of (qubit, negated?) where negated means
    # the literal is (NOT var), so it's satisfied when var == 0.
    # A clause (l_a OR l_b OR l_c) is FALSE only when all literals are false.
    # We compute clause-satisfied ancilla c_k = 1 iff clause k is satisfied.
    clauses = [
        [(x0, True), (x1, False), (x2, False)],   # (NOT x0 OR x1 OR x2)
        [(x0, True), (x1, False), (x2, True)],    # (NOT x0 OR x1 OR NOT x2)
        [(x0, False), (x1, True), (x2, True)],    # (x0 OR NOT x1 OR NOT x2)
        [(x0, True), (x1, True), (x2, True)],     # (NOT x0 OR NOT x1 OR NOT x2)
    ]

    def compute_clause(lits, target):
        # Set target = 0 initially (ancillas start at 0). Clause is false iff every
        # literal is false. Literal (q, neg): false when q == (0 if not neg else 1),
        # i.e. false when the value making it true is absent.
        # We detect the all-false condition, then flip target to 1 for satisfied.
        # For each literal, we want the "make-true" value on the qubit: neg -> 0, else -> 1.
        # Apply X to qubits whose make-true value is 0, so that all-controls-1 == all-literals-false-... 
        # We instead detect all-false: literal false when q == make_false_value.
        # make_false for (q,neg): q==1 if neg (var true makes NOT var false); q==0 if not neg.
        for q, neg in lits:
            if not neg:
                qc.x(q)  # now q==1 means literal was false
        # now for each literal q==1 means false; for neg literals q==1 already means false
        qc.mcx([q for q, _ in lits], target)  # target=1 iff all literals false (clause unsat)
        qc.x(target)  # target=1 iff clause satisfied
        for q, neg in lits:
            if not neg:
                qc.x(q)

    def uncompute_clause(lits, target):
        for q, neg in lits:
            if not neg:
                qc.x(q)
        qc.x(target)
        qc.mcx([q for q, _ in lits], target)
        for q, neg in lits:
            if not neg:
                qc.x(q)

    for k, lits in enumerate(clauses):
        compute_clause(lits, c[k])

    qc.mcx(c, out)      # out = 1 iff all clauses satisfied
    qc.z(out)           # phase -1 iff satisfied
    qc.mcx(c, out)      # uncompute out

    for k in range(len(clauses) - 1, -1, -1):
        uncompute_clause(clauses[k], c[k])
