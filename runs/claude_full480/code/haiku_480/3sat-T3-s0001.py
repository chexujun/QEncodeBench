from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    x = problem_qubits
    a = ancilla_qubits
    
    # Define conditions for each clause to be FALSE
    # Each clause is an OR of 3 literals; it is false iff all literals are false
    clause_false_conditions = [
        [-3, 4, 7],        # Clause 0: (x3 OR NOT x4 OR NOT x7) false iff NOT x3 AND x4 AND x7
        [-2, -4, 7],       # Clause 1: (x2 OR x4 OR NOT x7) false iff NOT x2 AND NOT x4 AND x7
        [-2, -3, -6],      # Clause 2: (x2 OR x3 OR x6) false iff NOT x2 AND NOT x3 AND NOT x6
        [-2, 3, -6],       # Clause 3: (x2 OR NOT x3 OR x6) false iff NOT x2 AND x3 AND NOT x6
        [1, 4, -5],        # Clause 4: (NOT x1 OR NOT x4 OR x5) false iff x1 AND x4 AND NOT x5
        [-3, -6, -7],      # Clause 5: (x3 OR x6 OR x7) false iff NOT x3 AND NOT x6 AND NOT x7
        [0, 3, 4]          # Clause 6: (NOT x0 OR NOT x3 OR NOT x4) false iff x0 AND x3 AND x4
    ]
    
    # Step 1: Compute whether each clause is false into its ancilla
    for clause_idx, clause_conds in enumerate(clause_false_conditions):
        controls = []
        need_flip = []
        
        for lit in clause_conds:
            if lit > 0:
                controls.append(lit)
                need_flip.append(False)
            else:
                controls.append(-lit)
                need_flip.append(True)
        
        # Apply X for negative literals (compute NOT)
        for ctrl, flip in zip(controls, need_flip):
            if flip:
                qc.x(x[ctrl])
        
        # Compute AND into ancilla
        qc.mcx(controls=[x[c] for c in controls], target_qubit=a[clause_idx])
        
        # Reverse X gates
        for ctrl, flip in zip(controls, need_flip):
            if flip:
                qc.x(x[ctrl])
    
    # Step 2: Compute whether all clauses are satisfied
    # all_satisfied = NOT(any clause is false) = AND of (NOT clause_false[i])
    # Initialize a[7] to 1
    qc.x(a[7])
    
    # Use ccx(a[i], a[7], a[7]) to compute: a[7] := a[7] AND (NOT a[i])
    for i in range(7):
        qc.ccx(a[i], a[7], a[7])
    
    # Step 3: Apply phase -1 when all clauses are satisfied
    qc.z(a[7])
    
    # Step 4: Uncompute the AND
    for i in range(6, -1, -1):
        qc.ccx(a[i], a[7], a[7])
    
    # Uncompute a[7] initialization
    qc.x(a[7])
    
    # Step 5: Uncompute clause falsity values (reverse order)
    for clause_idx in range(6, -1, -1):
        clause_conds = clause_false_conditions[clause_idx]
        
        controls = []
        need_flip = []
        
        for lit in clause_conds:
            if lit > 0:
                controls.append(lit)
                need_flip.append(False)
            else:
                controls.append(-lit)
                need_flip.append(True)
        
        # Apply X for negative literals
        for ctrl, flip in zip(controls, need_flip):
            if flip:
                qc.x(x[ctrl])
        
        # Uncompute AND
        qc.mcx(controls=[x[c] for c in controls], target_qubit=a[clause_idx])
        
        # Reverse X gates
        for ctrl, flip in zip(controls, need_flip):
            if flip:
                qc.x(x[ctrl])
