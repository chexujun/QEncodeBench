from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    pattern = "011101"
    fixed = [(i, int(c)) for i, c in enumerate(pattern) if c in "01"]

    flipped = []
    for i, bit in fixed:
        q = problem_qubits[i]
        if bit == 0:
            qc.x(q)
            flipped.append(q)

    ctrls = [problem_qubits[i] for i, _ in fixed]
    anc = ancilla_qubits[0]

    qc.mcx(ctrls, anc)
    qc.z(anc)
    qc.mcx(ctrls, anc)

    for q in flipped:
        qc.x(q)
