def build_oracle(qc, problem_qubits, ancilla_qubits):
    x = problem_qubits
    a = ancilla_qubits
    
    # Clause 1: (NOT x1 OR NOT x3 OR NOT x4) = NOT(x1 AND x3 AND x4)
    qc.mcx([x[1], x[3], x[4]], a[0])
    qc.x(a[0])
    
    # Clause 2: (NOT x3 OR NOT x4 OR x5) = NOT(x3 AND x4 AND NOT x5)
    qc.x(x[5])
    qc.mcx([x[3], x[4], x[5]], a[1])
    qc.x(x[5])
    qc.x(a[1])
    
    # Clause 3: (NOT x0 OR NOT x2 OR NOT x5) = NOT(x0 AND x2 AND x5)
    qc.mcx([x[0], x[2], x[5]], a[2])
    qc.x(a[2])
    
    # Clause 4: (x0 OR x1 OR NOT x3) = NOT(NOT x0 AND NOT x1 AND x3)
    qc.x(x[0])
    qc.x(x[1])
    qc.mcx([x[0], x[1], x[3]], a[3])
    qc.x(x[0])
    qc.x(x[1])
    qc.x(a[3])
    
    # Clause 5: (NOT x2 OR x4 OR x5) = NOT(x2 AND NOT x4 AND NOT x5)
    qc.x(x[4])
    qc.x(x[5])
    qc.mcx([x[2], x[4], x[5]], a[4])
    qc.x(x[4])
    qc.x(x[5])
    qc.x(a[4])
    
    # AND all clauses: a[5] = a[0] AND a[1] AND a[2] AND a[3] AND a[4]
    qc.mcx([a[0], a[1], a[2], a[3], a[4]], a[5])
    
    # Apply phase: Z gate on a[5]
    qc.z(a[5])
    
    # Uncompute: reverse all operations
    qc.mcx([a[0], a[1], a[2], a[3], a[4]], a[5])
    
    # Uncompute clause 5
    qc.x(x[4])
    qc.x(x[5])
    qc.mcx([x[2], x[4], x[5]], a[4])
    qc.x(x[4])
    qc.x(x[5])
    qc.x(a[4])
    
    # Uncompute clause 4
    qc.x(x[0])
    qc.x(x[1])
    qc.mcx([x[0], x[1], x[3]], a[3])
    qc.x(x[0])
    qc.x(x[1])
    qc.x(a[3])
    
    # Uncompute clause 3
    qc.mcx([x[0], x[2], x[5]], a[2])
    qc.x(a[2])
    
    # Uncompute clause 2
    qc.x(x[5])
    qc.mcx([x[3], x[4], x[5]], a[1])
    qc.x(x[5])
    qc.x(a[1])
    
    # Uncompute clause 1
    qc.mcx([x[1], x[3], x[4]], a[0])
    qc.x(a[0])
