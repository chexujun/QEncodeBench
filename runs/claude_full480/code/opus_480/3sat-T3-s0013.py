from qiskit import QuantumCircuit
import math


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    px = problem_qubits

    # Clauses as lists of (variable_index, is_positive).
    clauses = [
        [(0, False), (2, False), (6, False)],
        [(1, False), (4, True),  (7, False)],
        [(0, False), (2, False), (4, True)],
        [(2, False), (6, True),  (7, True)],
        [(4, False), (5, False), (6, True)],
        [(1, False), (5, True),  (7, False)],
        [(0, True),  (2, True),  (7, False)],
        [(0, True),  (4, False), (7, True)],
        [(0, True),  (1, True),  (7, False)],
        [(3, False), (6, False), (7, False)],
    ]

    clause_ancillas = ancilla_qubits[:len(clauses)]  # 10 clause ancillas
    final_ancilla = ancilla_qubits[len(clauses)]      # 1 phase ancilla

    def compute_clause(clause, anc):
        # A clause (l0 OR l1 OR l2) is FALSE iff all literals false.
        # Literal (i, True) is false when x_i = 0; (i, False) false when x_i = 1.
        # Set anc = 1 iff clause is TRUE, via: anc starts 0,
        # compute AND of "literal-is-false" into anc using x-flips, then invert.
        ctrls = []
        flips = []
        for (i, pos) in clause:
            q = px[i]
            if pos:
                # literal true when x_i=1; "false" indicator needs x_i=0 -> flip
                qc.x(q)
                flips.append(q)
            ctrls.append(q)
        # anc = AND(all literal-false-indicators)
        qc.mcx(ctrls, anc)
        # undo flips
        for q in flips:
            qc.x(q)
        # anc currently = 1 iff clause FALSE; invert to get clause TRUE
        qc.x(anc)

    def uncompute_clause(clause, anc):
        qc.x(anc)
        ctrls = []
        flips = []
        for (i, pos) in clause:
            q = px[i]
            if pos:
                qc.x(q)
                flips.append(q)
            ctrls.append(q)
        qc.mcx(ctrls, anc)
        for q in flips:
            qc.x(q)

    # Compute all clause ancillas (each = 1 iff clause satisfied).
    for clause, anc in zip(clauses, clause_ancillas):
        compute_clause(clause, anc)

    # Phase -1 iff ALL clause ancillas are 1 (formula satisfied).
    # Use compute-into-final then Z, or directly a multi-controlled Z.
    qc.h(final_ancilla)
    qc.mcx(clause_ancillas, final_ancilla)
    qc.h(final_ancilla)

    # Uncompute all clause ancillas in reverse order.
    for clause, anc in zip(reversed(clauses), reversed(clause_ancillas)):
        uncompute_clause(clause, anc)
