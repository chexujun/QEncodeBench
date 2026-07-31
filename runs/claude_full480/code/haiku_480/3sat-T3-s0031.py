def build_oracle(qc, problem_qubits, ancilla_qubits):
    # Each clause is represented as a list of (qubit_idx, is_negated) tuples
    # is_negated = False means positive literal (x_i)
    # is_negated = True means negated literal (NOT x_i)
    clauses = [
        [(2, False), (4, False), (6, True)],   # (x2 OR x4 OR NOT x6)
        [(0, True), (3, True), (6, True)],    # (NOT x0 OR NOT x3 OR NOT x6)
        [(3, False), (4, True), (6, False)],  # (x3 OR NOT x4 OR x6)
        [(4, True), (5, False), (6, False)],  # (NOT x4 OR x5 OR x6)
        [(0, False), (3, False), (6, True)],  # (x0 OR x3 OR NOT x6)
        [(2, False), (5, False), (6, False)], # (x2 OR x5 OR x6)
        [(0, False), (5, True), (6, False)],  # (x0 OR NOT x5 OR x6)
        [(3, True), (5, False), (6, True)],   # (NOT x3 OR x5 OR NOT x6)
        [(0, True), (2, False), (6, False)],  # (NOT x0 OR x2 OR x6)
        [(2, False), (3, False), (6, True)],  # (x2 OR x3 OR NOT x6)
        [(4, False), (5, True), (6, False)],  # (x4 OR NOT x5 OR x6)
        [(0, False), (2, True), (5, True)],   # (x0 OR NOT x2 OR NOT x5)
    ]
    
    # COMPUTE PHASE: For each clause, compute whether it's satisfied into an ancilla
    for clause_idx, clause in enumerate(clauses):
        clause_ancilla = ancilla_qubits[clause_idx]
        
        # Prepare controls: flip qubits for positive literals
        # We compute NOT(clause) = AND(NOT lit_i) then negate
        for qubit_idx, is_negated in clause:
            if not is_negated:  # positive literal: need NOT x_i in the AND
                qc.x(problem_qubits[qubit_idx])
        
        # Multi-controlled X: ancilla flips iff all controls are |1>
        # This computes AND(NOT positive_lit_i AND NOT_lit_i)
        control_qubits = [problem_qubits[qubit_idx] for qubit_idx, _ in clause]
        qc.mcx(control_qubits, clause_ancilla)
        
        # Undo the X gates on positive literals
        for qubit_idx, is_negated in clause:
            if not is_negated:
                qc.x(problem_qubits[qubit_idx])
        
        # Negate to convert AND(NOT...) to OR (by De Morgan's law)
        qc.x(clause_ancilla)
    
    # AND all clause ancillas into the final result ancilla
    final_ancilla = ancilla_qubits[12]
    clause_ancillas = ancilla_qubits[:12]
    qc.mcx(clause_ancillas, final_ancilla)
    
    # PHASE: Apply phase gate (mark solutions with -1)
    qc.z(final_ancilla)
    
    # UNCOMPUTE PHASE: Reverse the operations to return ancillas to |0>
    
    # Undo the final AND
    qc.mcx(clause_ancillas, final_ancilla)
    
    # Undo each clause in reverse order
    for clause_idx in range(len(clauses) - 1, -1, -1):
        clause = clauses[clause_idx]
        clause_ancilla = ancilla_qubits[clause_idx]
        
        # Undo the negation
        qc.x(clause_ancilla)
        
        # Undo the X gates on positive literals
        for qubit_idx, is_negated in clause:
            if not is_negated:
                qc.x(problem_qubits[qubit_idx])
        
        # Undo the multi-controlled X
        control_qubits = [problem_qubits[qubit_idx] for qubit_idx, _ in clause]
        qc.mcx(control_qubits, clause_ancilla)
        
        # Undo the initial X gates on positive literals
        for qubit_idx, is_negated in clause:
            if not is_negated:
                qc.x(problem_qubits[qubit_idx])
