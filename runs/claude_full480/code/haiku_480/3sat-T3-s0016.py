def build_oracle(qc, problem_qubits, ancilla_qubits):
    from qiskit.circuit import QuantumCircuit
    
    # 3-SAT clauses as lists of (variable_index, is_negated)
    clauses = [
        [(2, True), (5, False), (6, True)],    # (NOT x2 OR x5 OR NOT x6)
        [(0, True), (1, True), (6, False)],    # (NOT x0 OR NOT x1 OR x6)
        [(0, False), (2, False), (4, False)],  # (x0 OR x2 OR x4)
        [(0, False), (3, False), (6, False)],  # (x0 OR x3 OR x6)
        [(2, False), (4, False), (5, True)],   # (x2 OR x4 OR NOT x5)
        [(3, False), (5, True), (6, False)],   # (x3 OR NOT x5 OR x6)
        [(2, True), (5, True), (6, False)],    # (NOT x2 OR NOT x5 OR x6)
        [(4, False), (5, False), (6, False)],  # (x4 OR x5 OR x6)
        [(2, False), (3, True), (5, False)],   # (x2 OR NOT x3 OR x5)
        [(0, False), (4, True), (5, False)],   # (x0 OR NOT x4 OR x5)
        [(0, True), (1, True), (2, True)],     # (NOT x0 OR NOT x1 OR NOT x2)
    ]
    
    clause_ancillas = ancilla_qubits[:11]
    temp_ancilla = ancilla_qubits[11]
    
    # Step 1: Compute each clause (clause_i is satisfied)
    # A clause (l0 OR l1 OR l2) is satisfied iff NOT(NOT l0 AND NOT l1 AND NOT l2)
    for clause_idx, clause in enumerate(clauses):
        var_indices = [lit[0] for lit in clause]
        is_negated = [lit[1] for lit in clause]
        
        # Flip qubits for positive literals (to compute AND of negated literals)
        for var_idx, is_neg in zip(var_indices, is_negated):
            if not is_neg:
                qc.x(problem_qubits[var_idx])
        
        # Compute AND of (negated) literals into clause_ancilla
        qc.mcx([problem_qubits[vid] for vid in var_indices], clause_ancillas[clause_idx])
        
        # Restore qubits
        for var_idx, is_neg in zip(var_indices, is_negated):
            if not is_neg:
                qc.x(problem_qubits[var_idx])
        
        # Flip ancilla to get "clause is satisfied" (NOT of "clause is not satisfied")
        qc.x(clause_ancillas[clause_idx])
    
    # Step 2: Compute AND of all clause satisfactions into temp_ancilla
    qc.mcx(clause_ancillas, temp_ancilla)
    
    # Step 3: Apply phase flip when all clauses are satisfied
    qc.z(temp_ancilla)
    
    # Step 4: Uncompute AND of all clauses
    qc.mcx(clause_ancillas, temp_ancilla)
    
    # Step 5: Uncompute each clause in reverse order
    for clause_idx in range(len(clauses) - 1, -1, -1):
        var_indices = [lit[0] for lit in clauses[clause_idx]]
        is_negated = [lit[1] for lit in clauses[clause_idx]]
        
        # Flip back
        qc.x(clause_ancillas[clause_idx])
        
        # Flip qubits for positive literals
        for var_idx, is_neg in zip(var_indices, is_negated):
            if not is_neg:
                qc.x(problem_qubits[var_idx])
        
        # Uncompute AND using mcx
        qc.mcx([problem_qubits[vid] for vid in var_indices], clause_ancillas[clause_idx])
        
        # Restore qubits
        for var_idx, is_neg in zip(var_indices, is_negated):
            if not is_neg:
                qc.x(problem_qubits[var_idx])
