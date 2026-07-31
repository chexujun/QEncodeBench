from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x = problem_qubits
    a = ancilla_qubits
    
    # Clause definitions: (pos_controls, neg_controls)
    # For each clause, we specify which problem qubits must be 1 (pos) and 0 (neg)
    # such that the clause is FALSE when all these conditions hold
    clauses = [
        ([1], [3, 7]),   # (NOT x1 OR x3 OR x7): false iff (x1 AND NOT x3 AND NOT x7)
        ([], [0, 2, 7]), # (x0 OR x2 OR x7): false iff (NOT x0 AND NOT x2 AND NOT x7)
        ([3], [4, 5]),   # (NOT x3 OR x4 OR NOT x5): false iff (x3 AND NOT x4 AND x5)
        ([3, 5], [6]),   # (NOT x3 OR NOT x5 OR NOT x6): false iff (x3 AND x5 AND x6)
        ([0, 1], [5]),   # (NOT x0 OR NOT x1 OR x5): false iff (x0 AND x1 AND NOT x5)
        ([4, 6], [7]),   # (NOT x4 OR NOT x6 OR x7): false iff (x4 AND x6 AND NOT x7)
        ([0, 4], [7]),   # (x0 OR x4 OR NOT x7): false iff (NOT x0 AND NOT x4 AND x7)
    ]
    
    # COMPUTE PHASE: compute clause values into ancillas a[0..6]
    for i, (pos, neg) in enumerate(clauses):
        # Flip neg qubits to detect zeros as ones
        for q in neg:
            qc.x(x[q])
        
        # Compute AND: sets a[i]=1 iff all controls are 1
        controls = [x[q] for q in pos] + [x[q] for q in neg]
        if controls:
            qc.mcx(controls, a[i])
        
        # Unflip neg qubits
        for q in neg:
            qc.x(x[q])
        
        # Negate: a[i] is now 1 iff clause i is TRUE
        qc.x(a[i])
    
    # AND all 7 clause results into a[7]
    qc.mcx([a[i] for i in range(7)], a[7])
    
    # PHASE: apply Z gate (phase -1) when all clauses are satisfied
    qc.z(a[7])
    
    # UNCOMPUTE PHASE
    # Undo the AND
    qc.mcx([a[i] for i in range(7)], a[7])
    
    # Undo clause computations in reverse order
    for i in range(6, -1, -1):
        pos, neg = clauses[i]
        
        # Negate back to false_condition
        qc.x(a[i])
        
        # Undo AND computation
        for q in neg:
            qc.x(x[q])
        
        controls = [x[q] for q in pos] + [x[q] for q in neg]
        if controls:
            qc.mcx(controls, a[i])
        
        for q in neg:
            qc.x(x[q])
