from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Define all 13 clauses as (variable_index, is_negated) tuples
    clauses = [
        [(1, True), (2, True), (3, False)],      # (NOT x1 OR NOT x2 OR x3)
        [(2, False), (3, False), (4, True)],     # (x2 OR x3 OR NOT x4)
        [(1, False), (2, False), (5, True)],     # (x1 OR x2 OR NOT x5)
        [(1, True), (3, False), (5, False)],     # (NOT x1 OR x3 OR x5)
        [(0, True), (3, False), (5, True)],      # (NOT x0 OR x3 OR NOT x5)
        [(0, True), (1, False), (2, False)],     # (NOT x0 OR x1 OR x2)
        [(0, True), (1, False), (3, False)],     # (NOT x0 OR x1 OR x3)
        [(2, False), (3, False), (5, True)],     # (x2 OR x3 OR NOT x5)
        [(3, False), (4, True), (5, False)],     # (x3 OR NOT x4 OR x5)
        [(0, True), (2, False), (5, False)],     # (NOT x0 OR x2 OR x5)
        [(0, False), (2, True), (3, False)],     # (x0 OR NOT x2 OR x3)
        [(0, True), (1, False), (5, True)],      # (NOT x0 OR x1 OR NOT x5)
        [(0, True), (1, True), (4, False)],      # (NOT x0 OR NOT x1 OR x4)
    ]
    
    clause_ancillas = ancilla_qubits[:13]
    temp_ancillas = ancilla_qubits[13:]
    
    # Compute whether each clause is satisfied
    for clause_idx, clause in enumerate(clauses):
        lit_a, lit_b, lit_c = clause
        
        # Compute if (lit_a OR lit_b OR lit_c) is satisfied
        # Method: compute NOT(NOT lit_a AND NOT lit_b AND NOT lit_c)
        # We'll compute the AND part, then negate
        
        q_a = problem_qubits[lit_a[0]]
        q_b = problem_qubits[lit_b[0]]
        q_c = problem_qubits[lit_c[0]]
        
        aux0 = temp_ancillas[0]
        aux1 = temp_ancillas[1]
        
        # Build (NOT lit_a) AND (NOT lit_b) AND (NOT lit_c)
        # For each literal: if is_negated=True then literal is NOT var, so NOT literal = var
        #                   if is_negated=False then literal is var, so NOT literal = NOT var
        
        # Compute (NOT lit_a) check
        if lit_a[1]:  # lit_a is negated, so NOT lit_a = q_a
            qc.cx(q_a, aux0)
        else:  # lit_a is not negated, so NOT lit_a = NOT q_a
            qc.x(q_a)
            qc.cx(q_a, aux0)
            qc.x(q_a)
        
        # Compute (NOT lit_b) AND aux0 -> aux1
        if lit_b[1]:  # NOT lit_b = q_b
            qc.ccx(aux0, q_b, aux1)
        else:  # NOT lit_b = NOT q_b
            qc.x(q_b)
            qc.ccx(aux0, q_b, aux1)
            qc.x(q_b)
        
        # Compute (NOT lit_c) AND aux1 -> clause_ancillas[clause_idx]
        if lit_c[1]:  # NOT lit_c = q_c
            qc.ccx(aux1, q_c, clause_ancillas[clause_idx])
        else:  # NOT lit_c = NOT q_c
            qc.x(q_c)
            qc.ccx(aux1, q_c, clause_ancillas[clause_idx])
            qc.x(q_c)
        
        # Flip result to get (lit_a OR lit_b OR lit_c)
        qc.x(clause_ancillas[clause_idx])
        
        # Uncompute aux1 and aux0
        if lit_b[1]:
            qc.ccx(aux0, q_b, aux1)
        else:
            qc.x(q_b)
            qc.ccx(aux0, q_b, aux1)
            qc.x(q_b)
        
        if lit_a[1]:
            qc.cx(q_a, aux0)
        else:
            qc.x(q_a)
            qc.cx(q_a, aux0)
            qc.x(q_a)
    
    # Apply Z gate controlled by all clause ancillas (multi-controlled phase)
    qc.mcp(3.141592653589793, clause_ancillas, temp_ancillas[0])
    
    # Uncompute clauses in reverse
    for clause_idx in range(len(clauses) - 1, -1, -1):
        clause = clauses[clause_idx]
        lit_a, lit_b, lit_c = clause
        
        q_a = problem_qubits[lit_a[0]]
        q_b = problem_qubits[lit_b[0]]
        q_c = problem_qubits[lit_c[0]]
        
        aux0 = temp_ancillas[0]
        aux1 = temp_ancillas[1]
        
        # Flip back
        qc.x(clause_ancillas[clause_idx])
        
        # Recompute aux1 and aux0 (mirrors of computation above)
        if lit_a[1]:
            qc.cx(q_a, aux0)
        else:
            qc.x(q_a)
            qc.cx(q_a, aux0)
            qc.x(q_a)
        
        if lit_b[1]:
            qc.ccx(aux0, q_b, aux1)
        else:
            qc.x(q_b)
            qc.ccx(aux0, q_b, aux1)
            qc.x(q_b)
        
        if lit_c[1]:
            qc.ccx(aux1, q_c, clause_ancillas[clause_idx])
        else:
            qc.x(q_c)
            qc.ccx(aux1, q_c, clause_ancillas[clause_idx])
            qc.x(q_c)
