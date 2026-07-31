from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    pattern = "111110"
    a = ancilla_qubits[0]
    fixed = [(problem_qubits[i], c) for i, c in enumerate(pattern) if c in "01"]
    controls = []
    for q, c in fixed:
        if c == "0":
            qc.x(q)
        controls.append(q)
    qc.h(a)
    qc.mcx(controls, a)
    qc.h(a)
    for q, c in fixed:
        if c == "0":
            qc.x(q)
