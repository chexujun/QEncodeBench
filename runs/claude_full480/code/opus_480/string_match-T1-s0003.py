from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    pattern = "0??010"
    fixed = [(i, int(c)) for i, c in enumerate(pattern) if c != '?']
    a = ancilla_qubits[0]

    controls = []
    for i, bit in fixed:
        q = problem_qubits[i]
        if bit == 0:
            qc.x(q)
        controls.append(q)

    qc.h(a)
    qc.mcx(controls, a)
    qc.h(a)

    for i, bit in fixed:
        if bit == 0:
            qc.x(problem_qubits[i])
