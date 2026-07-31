from qiskit import QuantumCircuit
import math


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x0, x1, x2, x3 = (problem_qubits[0], problem_qubits[1],
                      problem_qubits[2], problem_qubits[3])
    # ancilla_qubits[i] holds clause i satisfaction (i=0..3), [4] is phase target
    c0, c1, c2, c3, target = (ancilla_qubits[0], ancilla_qubits[1],
                              ancilla_qubits[2], ancilla_qubits[3],
                              ancilla_qubits[4])

    # Each clause is an OR of 3 literals. Compute clause_ancilla = 1 iff clause satisfied.
    # For clause (l_a OR l_b OR l_c): NOT clause = (NOT l_a AND NOT l_b AND NOT l_c).
    # Set literal-qubit so that value 1 means "literal is TRUE".
    # We compute NOT(clause) via mcx with all literals negated, then X to flip to clause.

    # clause definitions: (qubit, is_negated_literal)
    # literal TRUE when: positive var -> qubit==1 ; negated var (NOT x) -> qubit==0
    clauses = [
        [(x0, False), (x1, True), (x2, False)],   # x0 OR NOT x1 OR x2
        [(x0, True), (x1, True), (x2, True)],      # NOT x0 OR NOT x1 OR NOT x2
        [(x0, False), (x2, True), (x3, False)],    # x0 OR NOT x2 OR x3
        [(x0, True), (x1, False), (x3, False)],    # NOT x0 OR x1 OR x3
    ]
    clause_ancillas = [c0, c1, c2, c3]

    def compute_clause(clause, anc):
        # We want anc = OR of literals. Trick: anc starts at 0.
        # Flip qubits so that "literal TRUE" corresponds to qubit==1 uniformly,
        # then clause satisfied iff at least one is 1, i.e. NOT(all zero).
        # For a positive literal (need qubit==1 for true): leave as is.
        # For a negated literal (need qubit==0 for true): apply X so true->1.
        for (q, neg) in clause:
            if neg:
                qc.x(q)
        # Now literal-true == qubit==1. clause satisfied iff not all three are 0.
        # Compute all-zero indicator: X all, mcx onto anc, X all -> anc = AND(all==0).
        for (q, neg) in clause:
            qc.x(q)
        qc.mcx([q for (q, neg) in clause], anc)  # anc = 1 iff all three (flipped) ==1, i.e. originally all literal-false
        for (q, neg) in clause:
            qc.x(q)
        # anc now = 1 iff clause UNsatisfied. Flip to get satisfied.
        qc.x(anc)
        # restore literal flips
        for (q, neg) in clause:
            if neg:
                qc.x(q)

    def uncompute_clause(clause, anc):
        for (q, neg) in clause:
            if neg:
                qc.x(q)
        qc.x(anc)
        for (q, neg) in clause:
            qc.x(q)
        qc.mcx([q for (q, neg) in clause], anc)
        for (q, neg) in clause:
            qc.x(q)
        for (q, neg) in clause:
            if neg:
                qc.x(q)

    # compute all clauses
    for clause, anc in zip(clauses, clause_ancillas):
        compute_clause(clause, anc)

    # phase -1 iff all clauses satisfied: multi-controlled Z on target
    qc.h(target)
    qc.mcx(clause_ancillas, target)
    qc.h(target)

    # uncompute all clauses (reverse order)
    for clause, anc in reversed(list(zip(clauses, clause_ancillas))):
        uncompute_clause(clause, anc)
