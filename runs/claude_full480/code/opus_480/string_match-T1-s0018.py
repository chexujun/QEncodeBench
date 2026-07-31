from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    pattern = "?0?100"
    fixed = [(i, int(c)) for i, c in enumerate(pattern) if c != '?']
    ctrl_qubits = [problem_qubits[i] for i, _ in fixed]
    zero_positions = [problem_qubits[i] for i, b in fixed if b == 0]

    for q in zero_positions:
        qc.x(q)

    if len(ctrl_qubits) == 0:
        qc.z(problem_qubits[0])
        qc.x(problem_qubits[0])
        qc.z(problem_qubits[0])
    elif len(ctrl_qubits) == 1:
        qc.z(ctrl_qubits[0])
    else:
        qc.h(ctrl_qubits[-1])
        qc.mcx(ctrl_qubits[:-1], ctrl_qubits[-1], ancilla_qubits[0],
               mode="recursion")
        qc.h(ctrl_qubits[-1])

    for q in zero_positions:
        qc.x(q)
