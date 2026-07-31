import numpy as np
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits, ancilla_qubits) -> None:
    p = problem_qubits
    anc = ancilla_qubits

    # Each clause is a list of (var_index, negated?) triples.
    # Clause is satisfied unless ALL its literals are false.
    clauses = [
        [(1, True), (3, False), (7, False)],
        [(0, False), (2, False), (7, False)],
        [(3, True), (4, False), (5, True)],
        [(3, True), (5, True), (6, True)],
        [(0, True), (1, True), (5, False)],
        [(4, True), (6, True), (7, False)],
        [(0, False), (4, False), (7, True)],
    ]

    clause_anc = anc[:len(clauses)]      # one ancilla per clause
    final_anc = anc[len(clauses)]        # AND of all clause ancillas

    def compute_clause(clause, target):
        # A literal is TRUE when: (not negated and var==1) or (negated and var==0).
        # Clause TRUE = OR of literals. Compute via De Morgan:
        # clause = NOT( AND of (literal false) ).
        # literal false means: positive literal with var==0, or negative literal with var==1.
        # Flip each variable qubit so that "1" marks "literal is false".
        ctrls = []
        for (vi, neg) in clause:
            q = p[vi]
            if not neg:
                # positive literal false when var==0 -> flip so 1 means false
                qc.x(q)
            # negative literal false when var==1 -> already 1 means false
            ctrls.append(q)
        # target = AND(all literals false)
        qc.mcx(ctrls, target)
        # target now = 1 iff clause is UNSATISFIED. We want clause satisfied indicator.
        qc.x(target)  # target = 1 iff clause satisfied
        # restore flipped qubits
        for (vi, neg) in clause:
            if not neg:
                qc.x(p[vi])

    def uncompute_clause(clause, target):
        for (vi, neg) in clause:
            if not neg:
                qc.x(p[vi])
        qc.x(target)
        qc.mcx(ctrls_of(clause), target)
        for (vi, neg) in clause:
            if not neg:
                qc.x(p[vi])

    def ctrls_of(clause):
        return [p[vi] for (vi, _) in clause]

    # Compute all clause ancillas
    for cl, t in zip(clauses, clause_anc):
        compute_clause(cl, t)

    # final_anc = AND of all clause ancillas => formula satisfied
    qc.mcx(clause_anc, final_anc)

    # Phase flip when formula satisfied
    qc.z(final_anc)

    # Uncompute final_anc
    qc.mcx(clause_anc, final_anc)

    # Uncompute all clause ancillas (reverse order)
    for cl, t in zip(reversed(clauses), reversed(clause_anc)):
        uncompute_clause(cl, t)
