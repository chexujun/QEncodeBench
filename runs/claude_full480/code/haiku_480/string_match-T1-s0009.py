def build_oracle(qc, problem_qubits, ancilla_qubits):
    # Pattern: "100101" means positions 0,3,5 must be 1 and positions 1,2,4 must be 0
    # f(x) = 1 iff text matches pattern exactly
    
    ancilla = ancilla_qubits[0]
    scratch = ancilla_qubits[1]
    
    # Flip bits that must be 0 (positions 1, 2, 4) so all problem_qubits are 1 when pattern matches
    qc.x(problem_qubits[1])
    qc.x(problem_qubits[2])
    qc.x(problem_qubits[4])
    
    # Compute f(x) into ancilla: ancilla becomes 1 iff all problem_qubits are 1
    qc.mcx(problem_qubits, ancilla, ancilla_qubits=[scratch], mode='auto')
    
    # Apply phase -1 via Z gate on ancilla (only affects state when ancilla=1)
    qc.z(ancilla)
    
    # Uncompute: restore ancilla to 0 while preserving the phase
    qc.mcx(problem_qubits, ancilla, ancilla_qubits=[scratch], mode='auto')
    
    # Restore the flipped bits
    qc.x(problem_qubits[1])
    qc.x(problem_qubits[2])
    qc.x(problem_qubits[4])
