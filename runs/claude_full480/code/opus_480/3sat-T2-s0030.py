from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x = problem_qubits
    cl = ancilla_qubits[:6]
    out = ancilla_qubits[6]

    clauses = [
        [(0, True),  (2, False), (3, True)],
        [(0, False), (1, False), (2, True)],
        [(0, True),  (1, False), (2, False)],
        [(0, False), (1, False), (2, False)],
        [(0, False), (2, True),  (3, False)],
        [(0, False), (2, True),  (3, True)],
    ]

    def compute():
        for ci, clause in enumerate(clauses):
            neg = [lit for (v, isneg) in clause if isneg for lit in [v]]
            for v in neg:
                qc.x(x[v])
            ctrls = [x[v] for (v, _) in clause]
            qc.mcx(ctrls, cl[ci])
            qc.x(cl[ci])
            for v in neg:
                qc.x(x[v])

    def uncompute():
        for ci in reversed(range(len(clauses))):
            clause = clauses[ci]
            neg = [v for (v, isneg) in clause if isneg]
            for v in neg:
                qc.x(x[v])
            ctrls = [x[v] for (v, _) in clause]
            qc.x(cl[ci])
            qc.mcx(ctrls, cl[ci])
            for v in neg:
                qc.x(x[v])

    compute()
    qc.mcx(cl, out)
    qc.z(out)
    qc.mcx(cl, out)
    uncompute()
