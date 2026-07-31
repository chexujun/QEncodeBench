from qiskit import QuantumCircuit
import math

def build_oracle(qc, problem_qubits, ancilla_qubits):
    p = problem_qubits
    a = ancilla_qubits

    # Clauses as lists of (var_index, is_positive_literal)
    # is_positive_literal True means literal is x_i, False means NOT x_i.
    clauses = [
        [(1, False), (3, False), (5, False)],
        [(0, False), (1, False), (2, True)],
        [(1, False), (2, False), (5, False)],
        [(1, False), (4, True), (5, False)],
        [(0, False), (1, False), (5, True)],
        [(2, True), (4, False), (5, True)],
        [(2, False), (3, False), (4, False)],
    ]

    n_clauses = len(clauses)
    clause_anc = a[:n_clauses]  # 7 ancillas, one per clause
    final_anc = a[n_clauses]    # 8th ancilla holds AND of all clauses

    def compute_clause(clause, anc):
        # clause satisfied unless all literals false.
        # literal x_i false means qubit=0; literal NOT x_i false means qubit=1.
        # Flip inputs so that "all literals false" == "all controls 1", set anc=1 there,
        # then invert anc to get clause value, then unflip.
        # For a positive literal x_i: false when qubit=0 -> apply X so control=1 when false.
        # For a negative literal NOT x_i: false when qubit=1 -> control=1 already when false.
        for (vi, pos) in clause:
            if pos:
                qc.x(p[vi])
        ctrls = [p[vi] for (vi, pos) in clause]
        qc.mcx(ctrls, anc)   # anc = 1 iff all literals false
        qc.x(anc)            # anc = clause value (1 iff satisfied)
        for (vi, pos) in clause:
            if pos:
                qc.x(p[vi])

    def uncompute_clause(clause, anc):
        for (vi, pos) in clause:
            if pos:
                qc.x(p[vi])
        ctrls = [p[vi] for (vi, pos) in clause]
        qc.x(anc)
        qc.mcx(ctrls, anc)
        for (vi, pos) in clause:
            if pos:
                qc.x(p[vi])

    # Compute each clause value into its ancilla
    for i, clause in enumerate(clauses):
        compute_clause(clause, clause_anc[i])

    # AND of all clause ancillas into final ancilla
    qc.mcx(list(clause_anc), final_anc)

    # Phase flip when final ancilla == 1
    qc.z(final_anc)

    # Uncompute AND
    qc.mcx(list(clause_anc), final_anc)

    # Uncompute clause ancillas (reverse order)
    for i in reversed(range(n_clauses)):
        uncompute_clause(clauses[i], clause_anc[i])
