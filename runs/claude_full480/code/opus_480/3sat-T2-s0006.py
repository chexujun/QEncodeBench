from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    x = problem_qubits
    # One ancilla per clause holds that clause's truth value (1 = satisfied).
    c = ancilla_qubits[:5]
    out = ancilla_qubits[5]

    # A clause (l_a OR l_b OR l_c) is False iff all three literals are False.
    # Compute clause-ancilla = OR of literals via: set literals so that
    # NOT(clause) = AND of negated literals; then clause = NOT that AND.
    # We implement each clause into its ancilla using De Morgan:
    #   ancilla = 1 (start), flip to 0 iff all literals false.
    # Literal true condition: positive literal x_i true when qubit=1;
    # negative literal NOT x_i true when qubit=0.

    def clause(anc, lits):
        # lits: list of (qubit, negated) ; literal false condition marker
        # Literal is FALSE when: positive -> qubit==0 ; negative -> qubit==1.
        # We want anc = OR(literals) = NOT(all literals false).
        # Prepare controls that are 1 exactly when the literal is FALSE.
        # positive literal false when qubit==0 -> X then use as control.
        # negative literal false when qubit==1 -> use directly as control.
        ctrls = []
        flips = []
        for q, neg in lits:
            if not neg:
                qc.x(q)      # now q==1 means literal false
                flips.append(q)
            ctrls.append(q)
        qc.x(anc)                     # anc = 1
        qc.mcx(ctrls, anc)            # if all literals false, anc -> 0
        for q in flips:
            qc.x(q)                   # restore
        return ctrls, flips

    clauses = [
        [(x[0], False), (x[1], True),  (x[3], False)],
        [(x[0], True),  (x[1], True),  (x[3], False)],
        [(x[0], True),  (x[1], False), (x[3], False)],
        [(x[2], True),  (x[3], False), (x[4], False)],
        [(x[0], False), (x[2], False), (x[4], True)],
    ]

    # Compute all clause ancillas.
    for anc, lits in zip(c, clauses):
        clause(anc, lits)

    # Formula satisfied iff all clause ancillas are 1.
    qc.mcx(c, out)
    qc.z(out)
    qc.mcx(c, out)

    # Uncompute clause ancillas (mirror).
    for anc, lits in reversed(list(zip(c, clauses))):
        # inverse of clause: same self-inverse structure
        ctrls = []
        flips = []
        for q, neg in lits:
            if not neg:
                qc.x(q)
                flips.append(q)
            ctrls.append(q)
        qc.mcx(ctrls, anc)
        qc.x(anc)
        for q in flips:
            qc.x(q)
