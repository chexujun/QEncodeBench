def build_oracle(qc, problem_qubits, ancilla_qubits):
    # Define the AND conditions that make each clause FALSE
    false_conditions = [
        [(0, True), (1, False), (3, True)],      # Clause 1: NOT x0 AND x1 AND NOT x3
        [(0, False), (1, False), (3, True)],     # Clause 2: x0 AND x1 AND NOT x3
        [(0, False), (1, True), (3, True)],      # Clause 3: x0 AND NOT x1 AND NOT x3
        [(2, False), (3, True), (4, True)],      # Clause 4: x2 AND NOT x3 AND NOT x4
        [(0, True), (2, True), (4, False)],      # Clause 5: NOT x0 AND NOT x2 AND x4
    ]
    
    clause_ancillas = ancilla_qubits[0:5]
    result_ancilla = ancilla_qubits[5]
    
    # COMPUTE: Calculate if each clause is FALSE
    for clause_idx, condition in enumerate(false_conditions):
        clause_ancilla = clause_ancillas[clause_idx]
        
        # Apply X gates to negate problem qubits as needed
        for qubit_idx, is_negated in condition:
            if is_negated:
                qc.x(problem_qubits[qubit_idx])
        
        # Compute the AND condition into clause_ancilla
        qubits = [problem_qubits[cond[0]] for cond in condition]
        qc.mcx(qubits, clause_ancilla)
        
        # Restore problem qubits
        for qubit_idx, is_negated in condition:
            if is_negated:
                qc.x(problem_qubits[qubit_idx])
    
    # Convert from "clause is FALSE" to "clause is TRUE"
    for ca in clause_ancillas:
        qc.x(ca)
    
    # Compute AND of all clause ancillas
    qc.mcx(clause_ancillas, result_ancilla)
    
    # PHASE: Apply Z gate (phase -1 when result_ancilla = 1)
    qc.z(result_ancilla)
    
    # UNCOMPUTE
    qc.mcx(clause_ancillas, result_ancilla)
    
    # Restore clause ancillas
    for ca in clause_ancillas:
        qc.x(ca)
    
    # Uncompute each clause's FALSE condition
    for clause_idx, condition in enumerate(false_conditions):
        clause_ancilla = clause_ancillas[clause_idx]
        
        # Apply X gates
        for qubit_idx, is_negated in condition:
            if is_negated:
                qc.x(problem_qubits[qubit_idx])
        
        # Uncompute AND
        qubits = [problem_qubits[cond[0]] for cond in condition]
        qc.mcx(qubits, clause_ancilla)
        
        # Restore problem qubits
        for qubit_idx, is_negated in condition:
            if is_negated:
                qc.x(problem_qubits[qubit_idx])
