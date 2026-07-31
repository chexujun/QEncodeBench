from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    clauses = [
        [(0, True), (1, True), (2, True)],
        [(0, True), (1, False), (2, True)],
        [(0, True), (1, False), (2, False)],
        [(0, False), (1, True), (2, False)],
        [(0, False), (1, True), (2, True)],
    ]

    def compute():
        for k, clause in enumerate(clauses):
            anc = ancilla_qubits[k]
            neg = [problem_qubits[i] for (i, isneg) in clause if not isneg]
            for q in neg:
                qc.x(q)
            ctrls = [problem_qubits[i] for (i, _) in clause]
            qc.mcx(ctrls, anc)
            qc.x(anc)
            for q in neg:
                qc.x(q)

    final = ancilla_qubits[5]
    compute()
    qc.mcx([ancilla_qubits[k] for k in range(5)], final)
    qc.z(final)
    qc.mcx([ancilla_qubits[k] for k in range(5)], final)
    # uncompute (mirror)
    for k in reversed(range(5)):
        clause = clauses[k]
        anc = ancilla_qubits[k]
        neg = [problem_qubits[i] for (i, isneg) in clause if not isneg]
        for q in neg:
            qc.x(q)
        qc.x(anc)
        ctrls = [problem_qubits[i] for (i, _) in clause]
        qc.mcx(ctrls, anc)
        for q in neg:
            qc.x(q)
