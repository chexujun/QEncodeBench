from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    pattern = "11??01"
    fixed = [(i, int(c)) for i, c in enumerate(pattern) if c != '?']

    flips = [problem_qubits[i] for (i, b) in fixed if b == 0]
    for q in flips:
        qc.x(q)

    ctrls = [problem_qubits[i] for (i, b) in fixed]
    qc.h(ctrls[-1])
    qc.mcx(ctrls[:-1], ctrls[-1])
    qc.h(ctrls[-1])

    for q in flips:
        qc.x(q)
