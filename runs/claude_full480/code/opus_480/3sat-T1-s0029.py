from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    x0, x1, x2 = problem_qubits[0], problem_qubits[1], problem_qubits[2]
    c = [ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[2], ancilla_qubits[3]]
    out = ancilla_qubits[4]

    # Clause literals: (lit_var, negated?) triples
    # Clause 0: (NOT x0 OR x1 OR x2)
    # Clause 1: (x0 OR NOT x1 OR NOT x2)
    # Clause 2: (NOT x0 OR NOT x1 OR x2)
    # Clause 3: (NOT x0 OR x1 OR NOT x2)
    clauses = [
        [(x0, True),  (x1, False), (x2, False)],
        [(x0, False), (x1, True),  (x2, True)],
        [(x0, True),  (x1, True),  (x2, False)],
        [(x0, True),  (x1, False), (x2, True)],
    ]

    def compute_clause(cl, target):
        # OR of literals -> target. Compute via De Morgan:
        # clause is TRUE unless all literals are FALSE.
        # A literal (v, neg): literal TRUE iff (v==1) if not neg else (v==0).
        # Literal FALSE iff v == (1 if neg else 0).
        # Flip qubit so that "all literals false" == all-ones on the literal qubits.
        negs = [neg for (_, neg) in cl]
        qs = [v for (v, _) in cl]
        # We want indicator that literal is FALSE. Literal false when v == (0 if not neg else 1)? 
        # literal(v,neg): true iff v==1 xor neg? no.
        # neg=False: literal = v ; false when v==0.
        # neg=True:  literal = not v ; false when v==1.
        # So literal FALSE iff v == (0 if not neg else 1) i.e. v == int(neg).
        # For MCX to fire on all-false, set qubit to 1 when literal is false.
        # If int(neg)==0 (false when v==0): apply X so v flips to 1 when false.
        # If int(neg)==1 (false when v==1): already 1 when false.
        for (v, neg) in cl:
            if int(neg) == 0:
                qc.x(v)
        # Now each literal-qubit is 1 exactly when that literal is FALSE.
        # target = AND(all false) => clause false. Then invert to get clause true.
        qc.mcx(qs, target)
        qc.x(target)  # target now = clause TRUE
        # restore literal qubits
        for (v, neg) in cl:
            if int(neg) == 0:
                qc.x(v)

    # Compute each clause into its own ancilla
    for i in range(4):
        compute_clause(clauses[i], c[i])

    # out = AND of all clauses
    qc.mcx(c, out)

    # phase
    qc.z(out)

    # uncompute out
    qc.mcx(c, out)

    # uncompute clauses (mirror)
    for i in reversed(range(4)):
        compute_clause(clauses[i], c[i])
