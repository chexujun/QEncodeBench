from qiskit import QuantumCircuit
import numpy as np


def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    p = problem_qubits
    anc = ancilla_qubits

    # Clause list: each clause is list of (var_index, negated?)
    # negated? True means the literal is NOT x_i
    clauses = [
        [(3, False), (4, True), (5, False)],
        [(1, False), (2, True), (3, False)],
        [(0, True), (1, True), (2, True)],
        [(0, False), (1, True), (4, False)],
        [(1, True), (2, False), (4, False)],
        [(0, True), (1, False), (2, True)],
    ]

    clause_anc = anc[:6]   # one ancilla per clause holds clause truth
    final_anc = anc[6]     # holds AND of all clauses

    def compute_clause(clause, target):
        # A clause (l0 OR l1 OR l2) is False iff all literals are False.
        # Literal x_i is False when qubit==0 (if not negated) or qubit==1 (if negated).
        # Flip control qubits so that "literal False" -> control qubit == 1.
        # For non-negated literal: literal False when x_i==0, so apply X to map 0->1.
        # For negated literal: literal False when x_i==1, so control on 1 directly.
        ctrls = []
        for (vi, neg) in clause:
            if not neg:
                qc.x(p[vi])
            ctrls.append(p[vi])
        # target starts |0>. Set target=1 when NOT all-literals-false.
        # First set target = AND(all controls) = clause is False.
        qc.mcx(ctrls, target)
        # Now target = 1 iff clause False. We want target = clause truth = NOT that.
        qc.x(target)
        # Undo the X mapping on qubits
        for (vi, neg) in clause:
            if not neg:
                qc.x(p[vi])

    def uncompute_clause(clause, target):
        for (vi, neg) in clause:
            if not neg:
                qc.x(p[vi])
        qc.x(target)
        qc.mcx([p[vi] for (vi, neg) in clause], target)
        for (vi, neg) in clause:
            if not neg:
                qc.x(p[vi])

    # Compute all clause ancillas
    for c, t in zip(clauses, clause_anc):
        compute_clause(c, t)

    # final_anc = AND of all clause ancillas
    qc.mcx(clause_anc, final_anc)

    # Phase
    qc.z(final_anc)

    # Uncompute final_anc
    qc.mcx(clause_anc, final_anc)

    # Uncompute all clause ancillas (reverse order)
    for c, t in zip(reversed(clauses), reversed(clause_anc)):
        uncompute_clause(c, t)
