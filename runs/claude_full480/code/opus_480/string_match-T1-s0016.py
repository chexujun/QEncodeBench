from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    pattern = "01101"
    fixed = [(i, c) for i, c in enumerate(pattern) if c != '?']
    ctrl_qubits = [problem_qubits[i] for i, c in fixed]
    zero_positions = [problem_qubits[i] for i, c in fixed if c == '0']

    for q in zero_positions:
        qc.x(q)

    if len(ctrl_qubits) == 0:
        qc.z(problem_qubits[0])
        qc.x(problem_qubits[0])
        qc.z(problem_qubits[0])
    elif len(ctrl_qubits) == 1:
        qc.z(ctrl_qubits[0])
    else:
        a = ancilla_qubits[0]
        qc.mcx(ctrl_qubits[:-1], a)
        qc.cz(a, ctrl_qubits[-1])
        qc.mcx(ctrl_qubits[:-1], a)

    for q in zero_positions:
        qc.x(q)
