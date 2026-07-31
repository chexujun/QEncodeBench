def build_oracle(qc, problem_qubits, ancilla_qubits):
    a1 = ancilla_qubits[0]
    a2 = ancilla_qubits[1]
    
    # Compute: a1 = x_1 AND x_2
    qc.ccx(problem_qubits[1], problem_qubits[2], a1)
    
    # Flip x_3 to prepare for checking NOT(x_3)
    qc.x(problem_qubits[3])
    
    # Compute: a2 = a1 AND NOT(x_3)
    qc.ccx(a1, problem_qubits[3], a2)
    
    # Apply phase -1 if the pattern matches
    qc.z(a2)
    
    # Uncompute: reverse the computation to return ancillas to |0>
    qc.ccx(a1, problem_qubits[3], a2)
    qc.x(problem_qubits[3])
    qc.ccx(problem_qubits[1], problem_qubits[2], a1)
