import numpy as np
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    # 3-SAT clauses as (variable_index, is_negated) literals.
    # A clause is satisfied when at least one literal is True.
    clauses = [
        [(0, True), (1, False), (2, False)],
        [(0, False), (1, True), (2, True)],
        [(0, False), (1, False), (2, False)],
        [(0, False), (1, True), (2, False)],
        [(0, True), (1, True), (2, True)],
    ]

    clause_ancillas = ancilla_qubits[:len(clauses)]
    phase_ancilla = ancilla_qubits[len(clauses)]

    def compute():
        for clause, anc in zip(clauses, clause_ancillas):
            ctrls = []
            # For clause (l0 OR l1 OR l2): NOT satisfied iff all literals False.
            # Flip each variable so that "literal False" -> control qubit = 1,
            # then MCX sets anc = 1 when all literals are False.
            for var, negated in clause:
                q = problem_qubits[var]
                # literal = var if not negated else NOT var.
                # literal is False when: (not negated and var==0) or (negated and var==1).
                # We want control high on that condition.
                if not negated:
                    qc.x(q)  # var==0 -> 1
                ctrls.append(q)
            qc.mcx(ctrls, anc)  # anc = 1 iff clause UNsatisfied
            for var, negated in clause:
                q = problem_qubits[var]
                if not negated:
                    qc.x(q)  # restore
            qc.x(anc)  # anc = 1 iff clause satisfied

    compute()
    # All clauses satisfied iff all clause_ancillas == 1. Apply phase then.
    qc.h(phase_ancilla)
    qc.x(phase_ancilla)
    qc.mcx(clause_ancillas, phase_ancilla)
    qc.x(phase_ancilla)
    qc.h(phase_ancilla)
    # Uncompute clause ancillas (mirror of compute).
    for clause, anc in zip(clauses, clause_ancillas):
        qc.x(anc)
        for var, negated in clause:
            q = problem_qubits[var]
            if not negated:
                qc.x(q)
        qc.mcx([problem_qubits[var] for var, _ in clause], anc)
        for var, negated in clause:
            q = problem_qubits[var]
            if not negated:
                qc.x(q)
