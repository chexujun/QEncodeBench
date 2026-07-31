def build_oracle(qc, problem_qubits, ancilla_qubits):
    qc.z(problem_qubits[2])
