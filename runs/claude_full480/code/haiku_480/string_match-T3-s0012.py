from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    pattern = "0001"
    n = 8
    m = 4
    
    match_ancillas = ancilla_qubits[0:5]
    temp_ancilla = ancilla_qubits[5]
    
    # Compute: for each offset, determine if pattern matches at that offset
    for offset in range(n - m + 1):  # offsets 0 to 4
        match_anc = match_ancillas[offset]
        pattern_qubits = [problem_qubits[offset + i] for i in range(m)]
        
        # Pattern is "0001": positions 0,1,2 must be 0; position 3 must be 1
        # Flip qubits that should be 0 to make them 1 temporarily
        for i in range(3):
            qc.x(pattern_qubits[i])
        
        # Apply X to match_anc iff all pattern_qubits are 1
        # (i.e., iff NOT s[o] AND NOT s[o+1] AND NOT s[o+2] AND s[o+3])
        qc.mcx(pattern_qubits, match_anc)
        
        # Flip the flipped qubits back
        for i in range(3):
            qc.x(pattern_qubits[i])
    
    # Compute OR of all matches: temp = match[0] OR match[1] OR ... OR match[4]
    # Using the identity: OR(a,b,...) = NOT(AND(NOT a, NOT b, ...))
    
    # Step 1: Compute AND(NOT match[0], ..., NOT match[4]) into temp
    for match_anc in match_ancillas:
        qc.x(match_anc)
    
    qc.mcx(match_ancillas, temp_ancilla)
    
    for match_anc in match_ancillas:
        qc.x(match_anc)
    
    # Step 2: Flip temp to get OR
    qc.x(temp_ancilla)
    
    # Apply phase -1 if temp = 1 (i.e., if pattern matches at least one offset)
    qc.z(temp_ancilla)
    
    # Uncompute temp (reverse of step 2)
    qc.x(temp_ancilla)
    
    # Uncompute AND computation (reverse of step 1)
    for match_anc in match_ancillas:
        qc.x(match_anc)
    
    qc.mcx(match_ancillas, temp_ancilla)
    
    for match_anc in match_ancillas:
        qc.x(match_anc)
    
    # Uncompute match computations in reverse order
    for offset in range(n - m - 1, -1, -1):
        match_anc = match_ancillas[offset]
        pattern_qubits = [problem_qubits[offset + i] for i in range(m)]
        
        for i in range(3):
            qc.x(pattern_qubits[i])
        
        qc.mcx(pattern_qubits, match_anc)
        
        for i in range(3):
            qc.x(pattern_qubits[i])
