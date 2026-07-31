def build_oracle(qc, problem_qubits, ancilla_qubits):
    # Compute x[0] XOR x[1] into ancilla[0]
    qc.cx(problem_qubits[0], ancilla_qubits[0])
    qc.cx(problem_qubits[1], ancilla_qubits[0])
    
    # Compute NOT x[2] into ancilla[1]
    qc.x(ancilla_qubits[1])
    qc.cx(problem_qubits[2], ancilla_qubits[1])
    
    # Compute ancilla[0] AND ancilla[1] into ancilla[2]
    qc.ccx(ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[2])
    
    # Apply phase
    qc.z(ancilla_qubits[2])
    
    # Uncompute ancilla[2]
    qc.ccx(ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[2])
    
    # Uncompute ancilla[1]
    qc.cx(problem_qubits[2], ancilla_qubits[1])
    qc.x(ancilla_qubits[1])
    
    # Uncompute ancilla[0]
    qc.cx(problem_qubits[1], ancilla_qubits[0])
    qc.cx(problem_qubits[0], ancilla_qubits[0])
