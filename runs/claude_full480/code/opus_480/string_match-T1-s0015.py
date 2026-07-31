from qiskit import QuantumCircuit

def build_oracle(qc, problem_qubits, ancilla_qubits):
    pattern = "01010"
    fixed = [(i, int(c)) for i, c in enumerate(pattern) if c in "01"]
    controls = []
    for i, bit in fixed:
        q = problem_qubits[i]
        if bit == 0:
            qc.x(q)
        controls.append(q)
    a = ancilla_qubits[0]
    qc.mcx(controls, a)
    qc.z(a)
    qc.mcx(controls, a)
    for i, bit in fixed:
        if bit == 0:
            qc.x(problem_qubits[i])
