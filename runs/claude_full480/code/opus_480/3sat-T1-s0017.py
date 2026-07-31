from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x0, x1, x2 = problem_qubits[0], problem_qubits[1], problem_qubits[2]

    clauses = [
        [(x0, True), (x1, True), (x2, False)],
        [(x0, True), (x1, False), (x2, False)],
        [(x0, False), (x1, False), (x2, False)],
        [(x0, True), (x1, False), (x2, True)],
        [(x0, False), (x1, True), (x2, False)],
    ]

    clause_ancillas = ancilla_qubits[0:5]
    final_ancilla = ancilla_qubits[5]

    def compute_clauses():
        for (lits, anc) in zip(clauses, clause_ancillas):
            for (q, neg) in lits:
                if neg:
                    qc.x(q)
            ctrls = [q for (q, neg) in lits]
            qc.mcx(ctrls, anc)
            for (q, neg) in lits:
                if neg:
                    qc.x(q)
            qc.x(anc)

    compute_clauses()
    qc.mcx(clause_ancillas, final_ancilla)
    qc.z(final_ancilla)
    qc.mcx(clause_ancillas, final_ancilla)

    for (lits, anc) in zip(reversed(clauses), reversed(clause_ancillas)):
        qc.x(anc)
        for (q, neg) in lits:
            if neg:
                qc.x(q)
        ctrls = [q for (q, neg) in lits]
        qc.mcx(ctrls, anc)
        for (q, neg) in lits:
            if neg:
                qc.x(q)
