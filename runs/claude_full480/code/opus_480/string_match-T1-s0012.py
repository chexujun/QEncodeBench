from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    pattern = "0?01?"
    fixed = [(i, int(c)) for i, c in enumerate(pattern) if c != '?']
    ctrl_qubits = []
    for i, bit in fixed:
        q = problem_qubits[i]
        if bit == 0:
            qc.x(q)
        ctrl_qubits.append(q)
    a = ancilla_qubits[0]
    qc.h(a)
    qc.mcx(ctrl_qubits, a)
    qc.h(a)
    qc.mcx(ctrl_qubits, a)
    qc.h(a)
    for i, bit in fixed:
        if bit == 0:
            qc.x(problem_qubits[i])
