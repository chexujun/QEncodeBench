def build_oracle(qc, problem_qubits, ancilla_qubits):
    match_ancs = ancilla_qubits[0:5]
    or_anc = ancilla_qubits[5]
    
    # Conditions for each offset: match[o] = s[s_o] AND NOT s[s_o2] AND NOT s[s_o3]
    conditions = [
        (0, 2, 3),  # offset 0: pattern "1?00" at positions 0-3
        (1, 3, 4),  # offset 1: pattern "1?00" at positions 1-4
        (2, 4, 5),  # offset 2: pattern "1?00" at positions 2-5
        (3, 5, 6),  # offset 3: pattern "1?00" at positions 3-6
        (4, 6, 7),  # offset 4: pattern "1?00" at positions 4-7
    ]
    
    # Compute match ancillas: match_ancs[o] = s[s_o] AND NOT s[s_o2] AND NOT s[s_o3]
    for o, (s_o, s_o2, s_o3) in enumerate(conditions):
        # Flip the negated qubits for the AND computation
        qc.x(problem_qubits[s_o2])
        qc.x(problem_qubits[s_o3])
        
        # Compute AND using Toffoli gates
        qc.ccx(problem_qubits[s_o], problem_qubits[s_o2], match_ancs[o])
        qc.ccx(match_ancs[o], problem_qubits[s_o3], match_ancs[o])
        
        # Unflip the negated qubits
        qc.x(problem_qubits[s_o2])
        qc.x(problem_qubits[s_o3])
    
    # Compute OR: or_anc = match[0] OR match[1] OR match[2] OR match[3] OR match[4]
    # Using De Morgan: a OR b OR c = NOT(NOT a AND NOT b AND NOT c)
    
    # Flip all match ancillas
    for anc in match_ancs:
        qc.x(anc)
    
    # Compute AND of flipped matches into or_anc
    qc.mcx(match_ancs, or_anc)
    
    # Flip or_anc to convert AND to OR
    qc.x(or_anc)
    
    # Apply phase -1 for marked states
    qc.z(or_anc)
    
    # Uncompute OR (reverse order)
    qc.x(or_anc)
    qc.mcx(match_ancs, or_anc)
    
    # Flip matches back
    for anc in match_ancs:
        qc.x(anc)
    
    # Uncompute match ancillas (reverse order)
    for o in range(len(conditions) - 1, -1, -1):
        s_o, s_o2, s_o3 = conditions[o]
        
        qc.x(problem_qubits[s_o2])
        qc.x(problem_qubits[s_o3])
        
        qc.ccx(match_ancs[o], problem_qubits[s_o3], match_ancs[o])
        qc.ccx(problem_qubits[s_o], problem_qubits[s_o2], match_ancs[o])
        
        qc.x(problem_qubits[s_o2])
        qc.x(problem_qubits[s_o3])
