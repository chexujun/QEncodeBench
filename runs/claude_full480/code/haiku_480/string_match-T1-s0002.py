def build_oracle(qc, problem_qubits, ancilla_qubits):
    # Pattern: "000010"
    # Mark the state where bits are [0, 0, 0, 0, 1, 0]
    
    a = ancilla_qubits[0]
    
    # Compute: Invert qubits that should be 0
    qc.x(problem_qubits[0])
    qc.x(problem_qubits[1])
    qc.x(problem_qubits[2])
    qc.x(problem_qubits[3])
    qc.x(problem_qubits[5])
    
    # Set ancilla if all problem qubits are 1
    qc.mcx(problem_qubits, a, ancilla_qubits[1:])
    
    # Phase: Apply Z to flip the sign
    qc.z(a)
    
    # Uncompute: Restore ancilla
    qc.mcx(problem_qubits, a, ancilla_qubits[1:])
    
    # Undo the X gates
    qc.x(problem_qubits[0])
    qc.x(problem_qubits[1])
    qc.x(problem_qubits[2])
    qc.x(problem_qubits[3])
    qc.x(problem_qubits[5])
