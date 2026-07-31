import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x = problem_qubits
    # Each clause: (variable_index, is_positive_literal)
    clauses = [
        [(0, False), (4, False), (5, False)],
        [(2, False), (3, True), (4, True)],
        [(1, True), (3, False), (5, False)],
        [(0, False), (1, True), (2, True)],
        [(1, False), (3, False), (4, False)],
        [(0, False), (2, True), (4, False)],
        [(1, False), (3, True), (4, False)],
        [(0, False), (1, True), (3, True)],
        [(0, False), (3, True), (5, True)],
        [(1, True), (4, True), (5, True)],
    ]

    clause_ancillas = ancilla_qubits[:len(clauses)]   # 10 ancillas, one per clause
    final_ancilla = ancilla_qubits[len(clauses)]      # 1 ancilla for the AND phase

    def compute_clause(clause, anc):
        # A clause (l_a OR l_b OR l_c) is FALSE iff all literals are false.
        # A literal (var, positive): false when qubit == (0 if positive else 1).
        # Flip qubits so that "literal is false" corresponds to |1>, then the
        # clause is false iff all three are |1>; ccx sets anc=1 in that case.
        for var, pos in clause:
            if pos:
                qc.x(x[var])   # positive literal false when var==0 -> make it 1
        controls = [x[var] for var, _ in clause]
        qc.mcx(controls, anc)   # anc = 1 iff clause is unsatisfied
        for var, pos in clause:
            if pos:
                qc.x(x[var])
        qc.x(anc)   # anc = 1 iff clause is satisfied

    def uncompute_clause(clause, anc):
        qc.x(anc)
        for var, pos in clause:
            if pos:
                qc.x(x[var])
        controls = [x[var] for var, _ in clause]
        qc.mcx(controls, anc)
        for var, pos in clause:
            if pos:
                qc.x(x[var])

    # Compute each clause satisfaction into its ancilla.
    for clause, anc in zip(clauses, clause_ancillas):
        compute_clause(clause, anc)

    # AND of all clause ancillas -> final ancilla, then phase.
    qc.mcx(clause_ancillas, final_ancilla)
    qc.z(final_ancilla)
    qc.mcx(clause_ancillas, final_ancilla)

    # Uncompute clauses (reverse order).
    for clause, anc in zip(reversed(clauses), reversed(clause_ancillas)):
        uncompute_clause(clause, anc)
