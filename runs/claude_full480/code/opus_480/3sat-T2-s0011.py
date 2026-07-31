from qiskit import QuantumCircuit
import numpy as np


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x = problem_qubits
    cl = ancilla_qubits[:6]
    out = ancilla_qubits[6]

    # Clause literals: (var index, negated?)
    clauses = [
        [(1, True), (2, True), (5, True)],
        [(0, False), (3, False), (5, False)],
        [(1, False), (2, False), (4, True)],
        [(2, False), (3, False), (4, True)],
        [(1, True), (4, False), (5, True)],
        [(3, True), (4, True), (5, False)],
    ]

    def compute_clauses():
        for ci, clause in enumerate(clauses):
            neg_vars = [v for (v, neg) in clause if neg]
            # Flip negated literals so that "True literal" == qubit is 1
            for v in neg_vars:
                qc.x(x[v])
            # Clause is satisfied unless ALL literals are 0.
            # Compute NOR: set clause ancilla to 1 iff all three are 0.
            for (v, neg) in clause:
                qc.x(x[v])
            qc.mcx([x[v] for (v, neg) in clause], cl[ci])
            for (v, neg) in clause:
                qc.x(x[v])
            # cl[ci] == 1 means clause UNSATISFIED. Flip so 1 == satisfied.
            qc.x(cl[ci])
            # Restore negated vars
            for v in neg_vars:
                qc.x(x[v])

    compute_clauses()
    qc.mcx(cl, out)
    qc.z(out)
    qc.mcx(cl, out)

    # Uncompute clause ancillas (mirror)
    for ci in reversed(range(len(clauses))):
        clause = clauses[ci]
        neg_vars = [v for (v, neg) in clause if neg]
        for v in neg_vars:
            qc.x(x[v])
        qc.x(cl[ci])
        for (v, neg) in clause:
            qc.x(x[v])
        qc.mcx([x[v] for (v, neg) in clause], cl[ci])
        for (v, neg) in clause:
            qc.x(x[v])
        for v in neg_vars:
            qc.x(x[v])
