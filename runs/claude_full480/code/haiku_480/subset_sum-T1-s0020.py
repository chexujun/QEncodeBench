def build_oracle(qc, problem_qubits, ancilla_qubits):
    phase_qubit = ancilla_qubits[0]
    
    # Compute predicate: f(x) = 1 iff the sum of selected elements equals 9.
    # With a = [4, 6, 3], this is true iff:
    # problem_qubits[0] = 0, problem_qubits[1] = 1, problem_qubits[2] = 1
    # (selecting a[1] + a[2] = 6 + 3 = 9)
    
    # Flip problem_qubits[0] to check if it's originally 0
    qc.x(problem_qubits[0])
    
    # Set phase_qubit to 1 iff all three qubits are now 1
    qc.mcx([problem_qubits[0], problem_qubits[1], problem_qubits[2]], phase_qubit)
    
    # Apply phase -1 iff phase_qubit is 1 (f(x) = 1)
    qc.z(phase_qubit)
    
    # Uncompute: reverse the MCX
    qc.mcx([problem_qubits[0], problem_qubits[1], problem_qubits[2]], phase_qubit)
    
    # Unflip problem_qubits[0] to restore its original value
    qc.x(problem_qubits[0])
