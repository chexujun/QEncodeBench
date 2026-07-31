from qiskit import QuantumCircuit
import math


def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    x = problem_qubits

    # Clause definitions: each clause is a list of (variable_index, negated?)
    # A clause (l0 OR l1 OR l2) is FALSE iff all literals are false.
    # We compute clause_ok = OR of literals into a clause-ancilla, using the
    # identity: clause is satisfied unless every literal is false.
    clauses = [
        [(1, False), (2, False), (4, False)],
        [(1, False), (2, False), (3, False)],
        [(0, True), (5, True), (6, True)],
        [(3, False), (5, True), (6, True)],
        [(0, True), (2, True), (5, False)],
        [(0, False), (2, True), (7, False)],
        [(0, False), (3, True), (7, True)],
        [(1, True), (3, False), (5, False)],
        [(0, False), (2, False), (3, False)],
        [(0, False), (1, False), (3, False)],
    ]

    clause_ancillas = ancilla_qubits[:10]   # one per clause
    final_ancilla = ancilla_qubits[10]      # AND of all clauses

    def compute_clause(clause, target):
        # target starts |0>. Set target = clause_satisfied.
        # A literal is TRUE when: (not negated and qubit==1) or (negated and qubit==0).
        # Flip qubit for negated literals so that literal-true <=> qubit==1.
        for (idx, neg) in clause:
            if neg:
                qc.x(x[idx])
        # Now clause satisfied iff at least one of the (possibly flipped) qubits is 1.
        # target = NOT(all zero). Compute all-zero via: X on each, MCX, then it's 1 iff all were 0.
        ctrls = [x[idx] for (idx, neg) in clause]
        for c in ctrls:
            qc.x(c)
        qc.mcx(ctrls, target)   # target = 1 iff all (flipped) literals were 0 = clause UNsatisfied
        for c in ctrls:
            qc.x(c)
        qc.x(target)            # target = 1 iff clause satisfied
        # restore negations
        for (idx, neg) in clause:
            if neg:
                qc.x(x[idx])

    # Compute all clause ancillas
    for cl, anc in zip(clauses, clause_ancillas):
        compute_clause(cl, anc)

    # final_ancilla = AND of all clause ancillas
    qc.mcx(clause_ancillas, final_ancilla)

    # Phase flip
    qc.z(final_ancilla)

    # Uncompute final_ancilla
    qc.mcx(clause_ancillas, final_ancilla)

    # Uncompute clause ancillas (mirror)
    for cl, anc in reversed(list(zip(clauses, clause_ancillas))):
        compute_clause(cl, anc)
