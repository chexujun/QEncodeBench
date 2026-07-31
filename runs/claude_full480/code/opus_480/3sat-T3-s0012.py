import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x = problem_qubits
    # Each clause: list of (var_index, is_positive)
    clauses = [
        [(0, False), (1, True), (2, False)],
        [(1, False), (3, True), (4, True)],
        [(0, False), (3, True), (5, False)],
        [(0, False), (4, False), (5, False)],
        [(1, True), (4, False), (5, False)],
        [(0, True), (2, True), (3, False)],
        [(0, False), (3, False), (5, False)],
        [(0, True), (1, True), (2, False)],
        [(0, False), (1, True), (4, False)],
        [(0, True), (3, True), (4, False)],
        [(1, True), (2, True), (5, True)],
        [(0, False), (3, True), (4, False)],
    ]
    clause_ancillas = ancilla_qubits[:12]
    final_ancilla = ancilla_qubits[12]

    def compute_clauses():
        for c, anc in zip(clauses, clause_ancillas):
            neg = [x[v] for (v, pos) in c if pos]
            for q in neg:
                qc.x(q)
            ctrls = [x[v] for (v, pos) in c]
            qc.mcx(ctrls, anc)
            qc.x(anc)
            for q in neg:
                qc.x(q)

    def uncompute_clauses():
        for c, anc in zip(clauses, clause_ancillas):
            neg = [x[v] for (v, pos) in c if pos]
            for q in neg:
                qc.x(q)
            qc.x(anc)
            qc.mcx([x[v] for (v, pos) in c], anc)
            for q in neg:
                qc.x(q)

    compute_clauses()
    qc.mcx(clause_ancillas, final_ancilla)
    qc.z(final_ancilla)
    qc.mcx(clause_ancillas, final_ancilla)
    uncompute_clauses()
