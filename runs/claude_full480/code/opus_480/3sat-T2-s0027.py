from qiskit import QuantumCircuit
import numpy as np


def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    p = problem_qubits
    anc = ancilla_qubits

    clauses = [
        [(3, False), (4, False), (5, False)],
        [(1, True),  (2, False), (4, True)],
        [(1, False), (3, False), (4, True)],
        [(1, True),  (3, False), (4, False)],
        [(1, False), (3, True),  (4, False)],
        [(0, False), (3, True),  (5, False)],
    ]

    clause_anc = anc[:6]
    final_anc = anc[6]

    def compute_clause(clause, target):
        # target = OR of literals. Literal true when qubit == polarity.
        # Compute NOR into target via De Morgan: flip inputs so that
        # "literal false" corresponds to control=1, then MCX sets target
        # when all literals false, then X to get OR.
        for var, pol in clause:
            if pol:
                qc.x(p[var])  # now p==1 means literal false
        qc.mcx([p[var] for var, _ in clause], target)
        for var, pol in clause:
            if pol:
                qc.x(p[var])
        qc.x(target)  # target = OR of literals

    # Compute all clauses
    for i, clause in enumerate(clauses):
        compute_clause(clause, clause_anc[i])

    # final_anc = AND of all clauses
    qc.mcx(clause_anc, final_anc)

    # phase
    qc.z(final_anc)

    # uncompute final_anc
    qc.mcx(clause_anc, final_anc)

    # uncompute clauses in reverse
    for i in reversed(range(len(clauses))):
        compute_clause(clauses[i], clause_anc[i])
