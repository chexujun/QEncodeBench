from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x = problem_qubits
    clause_ancillas = ancilla_qubits[:11]
    and_ancilla = ancilla_qubits[11]
    
    # Define the 11 clauses as (sign_a, var_a, sign_b, var_b, sign_c, var_c)
    # where sign=True means positive, sign=False means negated
    clauses = [
        (False, 4, True, 6, True, 7),      # (NOT x4 OR x6 OR x7)
        (False, 2, False, 3, False, 5),    # (NOT x2 OR NOT x3 OR NOT x5)
        (False, 0, False, 6, False, 7),    # (NOT x0 OR NOT x6 OR NOT x7)
        (False, 1, True, 2, True, 7),      # (NOT x1 OR x2 OR x7)
        (True, 4, False, 5, False, 6),     # (x4 OR NOT x5 OR NOT x6)
        (False, 2, False, 4, False, 5),    # (NOT x2 OR NOT x4 OR NOT x5)
        (False, 1, False, 4, True, 5),     # (NOT x1 OR NOT x4 OR x5)
        (False, 3, True, 4, False, 6),     # (NOT x3 OR x4 OR NOT x6)
        (False, 1, True, 3, True, 7),      # (NOT x1 OR x3 OR x7)
        (False, 3, True, 4, True, 5),      # (NOT x3 OR x4 OR x5)
        (True, 0, False, 4, True, 7),      # (x0 OR NOT x4 OR x7)
    ]
    
    # Compute each clause into its ancilla
    for i, (sign_a, var_a, sign_b, var_b, sign_c, var_c) in enumerate(clauses):
        c = clause_ancillas[i]
        qc.x(c)  # Initialize to 1
        
        # Flip literals that are negated (to check their "false" state)
        if not sign_a:
            qc.x(x[var_a])
        if not sign_b:
            qc.x(x[var_b])
        if not sign_c:
            qc.x(x[var_c])
        
        # If all three literals are "true", the clause is false; flip c
        qc.mcx([x[var_a], x[var_b], x[var_c]], c)
        
        # Restore flipped literals
        if not sign_c:
            qc.x(x[var_c])
        if not sign_b:
            qc.x(x[var_b])
        if not sign_a:
            qc.x(x[var_a])
    
    # Compute AND of all clauses
    qc.mcx(clause_ancillas, and_ancilla)
    
    # Apply phase: -1 iff all clauses are satisfied
    qc.z(and_ancilla)
    
    # Uncompute AND
    qc.mcx(clause_ancillas, and_ancilla)
    
    # Uncompute each clause (reverse order)
    for i in range(len(clauses) - 1, -1, -1):
        sign_a, var_a, sign_b, var_b, sign_c, var_c = clauses[i]
        c = clause_ancillas[i]
        
        if not sign_a:
            qc.x(x[var_a])
        if not sign_b:
            qc.x(x[var_b])
        if not sign_c:
            qc.x(x[var_c])
        
        qc.mcx([x[var_a], x[var_b], x[var_c]], c)
        
        if not sign_c:
            qc.x(x[var_c])
        if not sign_b:
            qc.x(x[var_b])
        if not sign_a:
            qc.x(x[var_a])
        
        qc.x(c)  # Restore c to 0
