def build_oracle(qc, problem_qubits, ancilla_qubits):
    import math
    
    x = problem_qubits
    a0, a1, a2, a3, a4 = ancilla_qubits
    
    # Compute clause violations
    
    # Clause 1: (x0 OR NOT x1 OR x2) violated iff (NOT x0) AND x1 AND (NOT x2)
    qc.x(x[0])
    qc.ccx(x[0], x[1], a4)
    qc.x(x[2])
    qc.ccx(a4, x[2], a0)
    qc.ccx(x[0], x[1], a4)
    qc.x(x[2])
    qc.x(x[0])
    
    # Clause 2: (NOT x0 OR NOT x1 OR NOT x2) violated iff x0 AND x1 AND x2
    qc.ccx(x[0], x[1], a4)
    qc.ccx(a4, x[2], a1)
    qc.ccx(x[0], x[1], a4)
    
    # Clause 3: (x0 OR NOT x2 OR x3) violated iff (NOT x0) AND x2 AND (NOT x3)
    qc.x(x[0])
    qc.ccx(x[0], x[2], a4)
    qc.x(x[3])
    qc.ccx(a4, x[3], a2)
    qc.ccx(x[0], x[2], a4)
    qc.x(x[3])
    qc.x(x[0])
    
    # Clause 4: (NOT x0 OR x1 OR x3) violated iff x0 AND (NOT x1) AND (NOT x3)
    qc.x(x[1])
    qc.ccx(x[0], x[1], a4)
    qc.x(x[3])
    qc.ccx(a4, x[3], a3)
    qc.ccx(x[0], x[1], a4)
    qc.x(x[3])
    qc.x(x[1])
    
    # Apply phase when all clauses are satisfied (all violations are 0)
    qc.x(a0)
    qc.x(a1)
    qc.x(a2)
    qc.x(a3)
    qc.mcp(math.pi, [a0, a1, a2, a3], x[0])
    qc.x(a3)
    qc.x(a2)
    qc.x(a1)
    qc.x(a0)
    
    # Uncompute clause violations
    
    # Clause 4 uncompute
    qc.x(x[1])
    qc.ccx(x[0], x[1], a4)
    qc.x(x[3])
    qc.ccx(a4, x[3], a3)
    qc.ccx(x[0], x[1], a4)
    qc.x(x[3])
    qc.x(x[1])
    
    # Clause 3 uncompute
    qc.x(x[0])
    qc.ccx(x[0], x[2], a4)
    qc.x(x[3])
    qc.ccx(a4, x[3], a2)
    qc.ccx(x[0], x[2], a4)
    qc.x(x[3])
    qc.x(x[0])
    
    # Clause 2 uncompute
    qc.ccx(x[0], x[1], a4)
    qc.ccx(a4, x[2], a1)
    qc.ccx(x[0], x[1], a4)
    
    # Clause 1 uncompute
    qc.x(x[0])
    qc.ccx(x[0], x[1], a4)
    qc.x(x[2])
    qc.ccx(a4, x[2], a0)
    qc.ccx(x[0], x[1], a4)
    qc.x(x[2])
    qc.x(x[0])
