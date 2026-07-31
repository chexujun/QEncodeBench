from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    x0, x1, x2, x3 = problem_qubits[0], problem_qubits[1], problem_qubits[2], problem_qubits[3]

    # Clauses: list of (qubit, negated) literals. Clause is OR of literals.
    # A clause is satisfied unless ALL literals are false.
    # literal (q, False) false when q==0 ; (q, True) false when q==1.
    clauses = [
        [(x0, False), (x1, False), (x2, True)],   # x0 OR x1 OR NOT x2
        [(x1, False), (x2, True), (x3, True)],    # x1 OR NOT x2 OR NOT x3
        [(x1, True), (x2, False), (x3, False)],   # NOT x1 OR x2 OR x3
        [(x0, True), (x2, True), (x3, False)],    # NOT x0 OR NOT x2 OR x3
        [(x0, False), (x2, False), (x3, True)],   # x0 OR x2 OR NOT x3
        [(x0, False), (x1, True), (x2, False)],   # x0 OR NOT x1 OR x2
    ]

    clause_ancillas = ancilla_qubits[:6]      # one per clause
    phase_ancilla = ancilla_qubits[6]

    def compute_clause(lits, target):
        # target should start at |0>. We set target = 1 iff clause satisfied.
        # Clause unsatisfied iff every literal false.
        # For literal (q, negated): literal is TRUE when q == (0 if negated else 1).
        # X the qubits so that "all literals false" maps to "all controls 1",
        # detect all-false into target (target=1 means all false), then flip target.
        ctrls = []
        for (q, negated) in lits:
            # literal false condition: q==1 if negated else q==0.
            # We want control=1 when literal is FALSE.
            if not negated:
                qc.x(q)   # now q==1 means original 0 => literal false
            ctrls.append(q)
        qc.mcx(ctrls, target)   # target=1 iff all literals false (clause unsat)
        qc.x(target)            # target=1 iff clause satisfied
        # undo the x on non-negated literals
        for (q, negated) in lits:
            if not negated:
                qc.x(q)

    def uncompute_clause(lits, target):
        for (q, negated) in lits:
            if not negated:
                qc.x(q)
        qc.x(target)
        qc.mcx([q for (q, _) in lits], target)
        for (q, negated) in lits:
            if not negated:
                qc.x(q)

    # compute all clause ancillas
    for lits, anc in zip(clauses, clause_ancillas):
        compute_clause(lits, anc)

    # phase: -1 iff all clause ancillas are 1
    qc.h(phase_ancilla)
    qc.mcx(clause_ancillas, phase_ancilla)
    qc.h(phase_ancilla)

    # uncompute all clause ancillas (reverse order)
    for lits, anc in zip(reversed(clauses), reversed(clause_ancillas)):
        uncompute_clause(lits, anc)
