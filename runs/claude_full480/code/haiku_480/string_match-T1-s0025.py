def build_oracle(qc, problem_qubits, ancilla_qubits):
    a = ancilla_qubits[0]
    
    # Pattern "?11?" requires s_1=1 AND s_2=1
    # Compute: set ancilla to (x1 AND x2)
    qc.ccx(problem_qubits[1], problem_qubits[2], a)
    # Phase: apply -1 if ancilla is 1
    qc.z(a)
    # Uncompute: reverse the computation, leaving ancilla at |0>
    qc.ccx(problem_qubits[1], problem_qubits[2], a)
