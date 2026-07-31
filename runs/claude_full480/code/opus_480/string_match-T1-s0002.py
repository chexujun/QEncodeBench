from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    pattern = "000010"
    fixed = [(i, int(c)) for i, c in enumerate(pattern) if c != '?']
    ctrl_qubits = []
    flipped = []
    for i, bit in fixed:
        q = problem_qubits[i]
        if bit == 0:
            qc.x(q)
            flipped.append(q)
        ctrl_qubits.append(q)
    a = ancilla_qubits[0]
    qc.h(a)
    qc.mcx(ctrl_qubits, a)
    qc.h(a)
    qc.mcx(ctrl_qubits, a)
    for q in flipped:
        qc.x(q)
