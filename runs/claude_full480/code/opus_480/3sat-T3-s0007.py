import math
from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x = problem_qubits

    # Clauses as lists of (variable_index, is_positive)
    clauses = [
        [(0, True),  (1, False), (2, False)],
        [(1, True),  (2, False), (4, False)],
        [(2, True),  (4, False), (5, False)],
        [(1, False), (3, True),  (5, False)],
        [(2, False), (3, True),  (5, True)],
        [(2, True),  (4, True),  (5, False)],
        [(3, False), (4, True),  (5, False)],
        [(0, True),  (2, True),  (6, True)],
        [(3, False), (4, False), (6, False)],
    ]

    clause_ancillas = ancilla_qubits[:len(clauses)]   # 9 ancillas, one per clause
    result_ancilla = ancilla_qubits[len(clauses)]     # 1 ancilla for the AND

    def compute_clause(clause, anc):
        # A clause (l0 OR l1 OR l2) is FALSE iff all literals are false.
        # Set anc = 1 iff clause is TRUE.
        # Flip the qubits so that "literal false" -> qubit is 1.
        # A literal (v, positive): false when x_v == 0 (positive) or x_v == 1 (negative).
        neg = []
        for v, pos in clause:
            if pos:
                qc.x(x[v])   # now qubit==1 means literal false
            neg.append(v)
        controls = [x[v] for v, _ in clause]
        # anc becomes 1 when NOT all-false. First set anc=1 if all-false, then X.
        qc.mcx(controls, anc)   # anc = 1 iff all literals false (clause false)
        qc.x(anc)               # anc = 1 iff clause true
        # undo the flips on problem qubits
        for v, pos in clause:
            if pos:
                qc.x(x[v])

    def uncompute_clause(clause, anc):
        for v, pos in clause:
            if pos:
                qc.x(x[v])
        qc.x(anc)
        controls = [x[v] for v, _ in clause]
        qc.mcx(controls, anc)
        for v, pos in clause:
            if pos:
                qc.x(x[v])

    # Compute all clause ancillas
    for clause, anc in zip(clauses, clause_ancillas):
        compute_clause(clause, anc)

    # AND of all clause ancillas -> result_ancilla, then phase
    qc.mcx(clause_ancillas, result_ancilla)
    qc.z(result_ancilla)
    qc.mcx(clause_ancillas, result_ancilla)

    # Uncompute all clause ancillas (reverse order)
    for clause, anc in zip(reversed(clauses), reversed(clause_ancillas)):
        uncompute_clause(clause, anc)
