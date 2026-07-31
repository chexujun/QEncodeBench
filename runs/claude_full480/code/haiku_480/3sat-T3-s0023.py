def build_oracle(qc, problem_qubits, ancilla_qubits):
    clause_ancillas = ancilla_qubits[0:7]
    final_ancilla = ancilla_qubits[7]
    
    # Define when each clause is unsatisfied (clause is 0 iff all conditions hold)
    conditions = [
        [(0, 1), (5, 1), (6, 0)],  # Clause 0: (NOT x0 OR NOT x5 OR x6)
        [(1, 0), (2, 1), (4, 0)],  # Clause 1: (x1 OR NOT x2 OR x4)
        [(0, 1), (2, 1), (7, 1)],  # Clause 2: (NOT x0 OR NOT x2 OR NOT x7)
        [(0, 1), (5, 1), (7, 1)],  # Clause 3: (NOT x0 OR NOT x5 OR NOT x7)
        [(0, 0), (2, 0), (5, 0)],  # Clause 4: (x0 OR x2 OR x5)
        [(4, 1), (6, 1), (7, 1)],  # Clause 5: (NOT x4 OR NOT x6 OR NOT x7)
        [(2, 0), (6, 1), (7, 1)],  # Clause 6: (x2 OR NOT x6 OR NOT x7)
    ]
    
    # COMPUTE: Set each clause ancilla to 1 if that clause is unsatisfied
    for clause_idx, cond in enumerate(conditions):
        c_anc = clause_ancillas[clause_idx]
        flipped = []
        controls = []
        
        for q_idx, val in cond:
            if val == 0:
                qc.x(problem_qubits[q_idx])
                flipped.append(q_idx)
            controls.append(problem_qubits[q_idx])
        
        qc.mcx(controls, c_anc)
        
        for q_idx in flipped:
            qc.x(problem_qubits[q_idx])
    
    # COMPUTE: Flip ancillas (1 = satisfied, 0 = unsatisfied)
    for c_anc in clause_ancillas:
        qc.x(c_anc)
    
    # COMPUTE: Set final_ancilla = AND of all clause ancillas
    qc.mcx(clause_ancillas, final_ancilla)
    
    # PHASE: Apply Z gate (phase -1 iff final_ancilla is 1)
    qc.z(final_ancilla)
    
    # UNCOMPUTE: Reverse in opposite order
    qc.mcx(clause_ancillas, final_ancilla)
    
    for c_anc in clause_ancillas:
        qc.x(c_anc)
    
    for clause_idx in range(len(conditions) - 1, -1, -1):
        cond = conditions[clause_idx]
        c_anc = clause_ancillas[clause_idx]
        
        flipped = []
        controls = []
        
        for q_idx, val in cond:
            if val == 0:
                qc.x(problem_qubits[q_idx])
                flipped.append(q_idx)
            controls.append(problem_qubits[q_idx])
        
        qc.mcx(controls, c_anc)
        
        for q_idx in flipped:
            qc.x(problem_qubits[q_idx])
