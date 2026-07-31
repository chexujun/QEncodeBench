def build_oracle(qc, problem_qubits, ancilla_qubits):
    pattern = [0, 0, 1, 0]
    n_offsets = 5
    
    match_flags = ancilla_qubits[:n_offsets]
    or_result = ancilla_qubits[5]
    
    # Compute match flags for each offset
    for offset in range(n_offsets):
        mf = match_flags[offset]
        controls = []
        
        # Flip qubits with negative parity (pattern[i] == 0)
        for i, p in enumerate(pattern):
            qubit = problem_qubits[offset + i]
            if p == 0:
                qc.x(qubit)
            controls.append(qubit)
        
        # Apply multi-controlled X to compute AND of all conditions
        qc.mcx(controls, mf)
        
        # Flip qubits back
        for i, p in enumerate(pattern):
            if p == 0:
                qc.x(problem_qubits[offset + i])
    
    # Compute OR of all match flags: OR = NOT(AND(NOT match_flags))
    for mf in match_flags:
        qc.x(mf)
    qc.mcx(match_flags, or_result)
    for mf in match_flags:
        qc.x(mf)
    qc.x(or_result)
    
    # Apply phase
    qc.z(or_result)
    
    # Uncompute OR
    qc.x(or_result)
    for mf in match_flags:
        qc.x(mf)
    qc.mcx(match_flags, or_result)
    for mf in match_flags:
        qc.x(mf)
    
    # Uncompute match flags
    for offset in range(n_offsets - 1, -1, -1):
        mf = match_flags[offset]
        controls = []
        
        for i, p in enumerate(pattern):
            qubit = problem_qubits[offset + i]
            if p == 0:
                qc.x(qubit)
            controls.append(qubit)
        
        qc.mcx(controls, mf)
        
        for i, p in enumerate(pattern):
            if p == 0:
                qc.x(problem_qubits[offset + i])
