from qiskit import QuantumCircuit
import numpy as np


def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    # Clause list: each clause is a list of (var_index, is_negated)
    clauses = [
        [(0, False), (2, False), (4, True)],
        [(0, True), (3, False), (5, True)],
        [(2, False), (3, True), (5, True)],
        [(2, True), (3, False), (6, True)],
        [(2, False), (4, False), (5, True)],
        [(0, False), (3, True), (7, True)],
        [(1, False), (2, True), (4, False)],
        [(2, True), (3, True), (5, False)],
        [(1, True), (2, False), (4, True)],
        [(0, True), (1, False), (2, True)],
    ]

    clause_ancillas = ancilla_qubits[:len(clauses)]  # 10 ancillas, one per clause
    final_ancilla = ancilla_qubits[len(clauses)]     # 11th ancilla for the phase

    def compute_clause(clause, anc):
        # A 3-literal OR clause is satisfied unless all literals are false.
        # Literal (v, neg): false when qubit == (0 if not neg else 1).
        # Flip qubits so that "all-false" corresponds to all-ones, use CCX,
        # then invert result so anc = OR(literals).
        lits = [problem_qubits[v] for (v, _) in clause]
        # For a positive literal, it is false when qubit==0 -> apply X so false->1.
        # For a negative literal, it is false when qubit==1 -> already 1.
        for (v, neg) in clause:
            if not neg:
                qc.x(problem_qubits[v])
        # Now each literal-false corresponds to its (possibly flipped) qubit == 1.
        # anc = AND of (literal-false) via CCX(mcx); this is 1 iff clause unsatisfied.
        qc.mcx(lits, anc)
        # anc currently = 1 iff clause unsatisfied. Flip to get clause-satisfied.
        qc.x(anc)
        # Restore problem qubits.
        for (v, neg) in clause:
            if not neg:
                qc.x(problem_qubits[v])

    def uncompute_clause(clause, anc):
        lits = [problem_qubits[v] for (v, _) in clause]
        for (v, neg) in clause:
            if not neg:
                qc.x(problem_qubits[v])
        qc.x(anc)
        qc.mcx(lits, anc)
        for (v, neg) in clause:
            if not neg:
                qc.x(problem_qubits[v])

    # Compute all clause results.
    for clause, anc in zip(clauses, clause_ancillas):
        compute_clause(clause, anc)

    # Phase -1 iff all clause ancillas are 1 (formula satisfied).
    qc.h(final_ancilla)
    qc.x(final_ancilla)
    qc.mcx(clause_ancillas, final_ancilla)
    qc.x(final_ancilla)
    qc.h(final_ancilla)

    # Uncompute all clause results.
    for clause, anc in zip(clauses, clause_ancillas):
        uncompute_clause(clause, anc)
