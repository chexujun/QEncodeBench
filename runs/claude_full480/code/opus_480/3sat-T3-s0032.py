from qiskit import QuantumCircuit
import math


def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    x = problem_qubits
    # Clauses as list of literals; each literal (var_index, is_positive)
    clauses = [
        [(4, False), (6, True), (7, True)],
        [(2, False), (3, False), (5, False)],
        [(0, False), (6, False), (7, False)],
        [(1, False), (2, True), (7, True)],
        [(4, True), (5, False), (6, False)],
        [(2, False), (4, False), (5, False)],
        [(1, False), (4, False), (5, True)],
        [(3, False), (4, True), (6, False)],
        [(1, False), (3, True), (7, True)],
        [(3, False), (4, True), (5, True)],
        [(0, True), (4, False), (7, True)],
    ]

    clause_ancillas = ancilla_qubits[:len(clauses)]  # 11 ancillas, one per clause
    final = ancilla_qubits[11]  # 12th ancilla for phase

    def compute_clause(clause, anc):
        # clause satisfied iff at least one literal true.
        # anc should end = clause value (1 if satisfied).
        # Compute NOT(clause) = AND of negated literals, into anc, then X.
        # For each literal (v, pos): literal true when qubit==pos.
        # negated literal true when qubit == (not pos).
        # We want anc = AND over literals of (qubit == not pos).
        # Set controls: for positive literal, control on qubit==0 -> need X before/after.
        ctrls = []
        flips = []
        for (v, pos) in clause:
            q = x[v]
            if pos:
                # literal true when q==1; negated true when q==0 -> control on 0: X wrap
                qc.x(q)
                flips.append(q)
            ctrls.append(q)
        qc.mcx(ctrls, anc)  # anc ^= AND(controls) = NOT(clause)
        for q in flips:
            qc.x(q)
        qc.x(anc)  # anc = clause value

    # compute all clauses
    for c, anc in zip(clauses, clause_ancillas):
        compute_clause(c, anc)

    # final = AND of all clause ancillas -> phase
    qc.h(final)
    qc.mcx(clause_ancillas, final)
    qc.h(final)

    # uncompute clauses in reverse
    for c, anc in zip(reversed(clauses), reversed(clause_ancillas)):
        compute_clause(c, anc)
