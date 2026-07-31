def build_oracle(qc, problem_qubits, ancilla_qubits):
    qc.x(problem_qubits[0])
    qc.z(problem_qubits[0])
    qc.x(problem_qubits[0])
