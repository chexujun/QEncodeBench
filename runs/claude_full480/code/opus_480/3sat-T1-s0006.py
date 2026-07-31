from qiskit import QuantumCircuit
import numpy as np


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x0, x1, x2 = problem_qubits[0], problem_qubits[1], problem_qubits[2]
    clause_anc = ancilla_qubits[:5]
    out = ancilla_qubits[5]

    # Each clause is a 3-literal OR. clause ancilla = OR of literals.
    # OR(a,b,c) computed as NOT(AND(NOT a, NOT b, NOT c)):
    # set literal qubit to value of literal, then ccx the negations.
    clauses = [
        [(x0, True), (x1, False), (x2, False)],   # (NOT x0 OR x1 OR x2)
        [(x0, False), (x1, False), (x2, True)],   # (x0 OR x1 OR NOT x2)
        [(x0, False), (x1, True), (x2, False)],   # (x0 OR NOT x1 OR x2)
        [(x0, True), (x1, False), (x2, True)],    # (NOT x0 OR x1 OR NOT x2)
        [(x0, True), (x1, True), (x2, False)],    # (NOT x0 OR NOT x1 OR x2)
    ]

    def compute_clause(clause, anc):
        # For a literal, it is TRUE when qubit == (not negated).
        # Negated literal (NOT x) is true when x==0.
        # We want anc = OR of literals = NOT(AND of (literal false)).
        # literal_i false means: for positive literal, x==0; for negated, x==1.
        # We flip qubits so that "literal false" corresponds to control==1,
        # AND them into anc (giving AND of literal-false), then X to negate.
        flips = []
        for q, negated in clause:
            # literal true condition: positive -> x==1 ; negated -> x==0
            # literal false condition: positive -> x==0 ; negated -> x==1
            # want control==1 when literal is FALSE
            if not negated:
                flips.append(q)  # positive: false when x==0 -> flip so 1 marks false
        for q, negated in clause:
            if not negated:
                qc.x(q)
        controls = [q for (q, _) in clause]
        qc.mcx(controls, anc)
        for q, negated in clause:
            if not negated:
                qc.x(q)
        qc.x(anc)  # anc = OR of literals

    def uncompute_clause(clause, anc):
        qc.x(anc)
        for q, negated in clause:
            if not negated:
                qc.x(q)
        controls = [q for (q, _) in clause]
        qc.mcx(controls, anc)
        for q, negated in clause:
            if not negated:
                qc.x(q)

    for cl, anc in zip(clauses, clause_anc):
        compute_clause(cl, anc)

    qc.h(out)
    qc.mcx(clause_anc, out)
    qc.h(out)

    for cl, anc in zip(clauses, clause_anc):
        uncompute_clause(cl, anc)
