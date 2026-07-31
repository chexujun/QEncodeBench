from qiskit import QuantumCircuit
import math


def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    x = problem_qubits

    # Clauses as lists of (variable_index, is_positive_literal)
    clauses = [
        [(0, True), (2, True), (4, True)],
        [(4, False), (6, True), (7, True)],
        [(0, True), (2, True), (7, True)],
        [(0, False), (2, False), (7, False)],
        [(0, True), (1, False), (2, False)],
        [(0, False), (3, True), (7, True)],
        [(2, True), (4, False), (7, True)],
        [(0, True), (6, False), (7, True)],
        [(3, True), (4, False), (6, True)],
        [(2, True), (6, True), (7, True)],
        [(1, True), (5, True), (7, False)],
    ]

    clause_ancillas = ancilla_qubits[:len(clauses)]
    final_ancilla = ancilla_qubits[len(clauses)]

    def compute_clauses():
        for clause, anc in zip(clauses, clause_ancillas):
            # Clause is satisfied unless all literals are false.
            # For a positive literal (var), it is false when var==0.
            # For a negative literal (NOT var), it is false when var==1.
            # Flip the variable qubits so that "clause unsatisfied" == all controls 1.
            neg_ctrls = []
            for var, positive in clause:
                if positive:
                    # literal false when var==0 -> flip so that var_false maps to 1
                    qc.x(x[var])
                    neg_ctrls.append(var)
            ctrls = [x[var] for var, _ in clause]
            # anc becomes 1 iff all literals false (clause unsatisfied)
            qc.mcx(ctrls, anc)
            # anc == 1 means unsatisfied; we want anc == 1 means satisfied -> flip
            qc.x(anc)
            # restore flipped variable qubits
            for var in neg_ctrls:
                qc.x(x[var])

    def uncompute_clauses():
        for clause, anc in reversed(list(zip(clauses, clause_ancillas))):
            neg_ctrls = []
            for var, positive in clause:
                if positive:
                    qc.x(x[var])
                    neg_ctrls.append(var)
            ctrls = [x[var] for var, _ in clause]
            qc.x(anc)
            qc.mcx(ctrls, anc)
            for var in neg_ctrls:
                qc.x(x[var])

    # Compute each clause ancilla = 1 iff its clause is satisfied.
    compute_clauses()

    # Phase -1 iff all clause ancillas are 1 (all clauses satisfied).
    qc.mcx(clause_ancillas, final_ancilla)
    qc.z(final_ancilla)
    qc.mcx(clause_ancillas, final_ancilla)

    # Uncompute clause ancillas.
    uncompute_clauses()
