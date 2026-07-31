def build_oracle(qc, problem_qubits, ancilla_qubits):
    # Compute pattern matches at each offset
    # Pattern is "0011"
    for offset in range(5):
        match_qubit = ancilla_qubits[offset]
        controls = [problem_qubits[offset], problem_qubits[offset+1], 
                    problem_qubits[offset+2], problem_qubits[offset+3]]
        # Mark when pattern "0011" is matched at this offset
        qc.mcx(controls, match_qubit, ctrl_state='0011')
    
    # Compute OR of all matches using NOT-AND-NOT
    # Compute NOT of each match
    for i in range(5):
        qc.x(ancilla_qubits[i])
    
    # Compute AND of NOT(matches) into ancilla 5
    # This equals NOT(OR(matches))
    qc.mcx([ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[2], 
            ancilla_qubits[3], ancilla_qubits[4]], ancilla_qubits[5])
    
    # Compute NOT to get OR
    qc.x(ancilla_qubits[5])
    
    # Apply phase
    qc.z(ancilla_qubits[5])
    
    # Uncompute in reverse order
    # Uncompute NOT to get AND again
    qc.x(ancilla_qubits[5])
    
    # Uncompute AND
    qc.mcx([ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[2], 
            ancilla_qubits[3], ancilla_qubits[4]], ancilla_qubits[5])
    
    # Uncompute NOT of matches
    for i in range(5):
        qc.x(ancilla_qubits[i])
    
    # Uncompute pattern matches
    for offset in range(4, -1, -1):
        match_qubit = ancilla_qubits[offset]
        controls = [problem_qubits[offset], problem_qubits[offset+1], 
                    problem_qubits[offset+2], problem_qubits[offset+3]]
        qc.mcx(controls, match_qubit, ctrl_state='0011')
