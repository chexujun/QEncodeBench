def build_oracle(qc, problem_qubits, ancilla_qubits):
    p = problem_qubits  # x0, x1, x2
    a = ancilla_qubits  # a0-a4
    
    # Compute clause 1: (x0 OR NOT x1 OR NOT x2) = NOT((NOT x0) AND x1 AND x2)
    qc.x(p[0])
    qc.ccx(p[0], p[1], a[4])
    qc.ccx(a[4], p[2], a[0])
    qc.ccx(p[0], p[1], a[4])
    qc.x(p[0])
    qc.x(a[0])
    
    # Compute clause 2: (NOT x0 OR NOT x1 OR x2) = NOT(x0 AND x1 AND (NOT x2))
    qc.x(p[2])
    qc.ccx(p[0], p[1], a[4])
    qc.ccx(a[4], p[2], a[1])
    qc.ccx(p[0], p[1], a[4])
    qc.x(p[2])
    qc.x(a[1])
    
    # Compute clause 3: (NOT x0 OR x1 OR x2) = NOT(x0 AND (NOT x1) AND (NOT x2))
    qc.x(p[1])
    qc.x(p[2])
    qc.ccx(p[0], p[1], a[4])
    qc.ccx(a[4], p[2], a[2])
    qc.ccx(p[0], p[1], a[4])
    qc.x(p[2])
    qc.x(p[1])
    qc.x(a[2])
    
    # Compute clause 4: (NOT x0 OR NOT x1 OR NOT x2) = NOT(x0 AND x1 AND x2)
    qc.ccx(p[0], p[1], a[4])
    qc.ccx(a[4], p[2], a[3])
    qc.ccx(p[0], p[1], a[4])
    qc.x(a[3])
    
    # Compute AND of all clauses into a[4]
    qc.mcx(control_qubits=[a[0], a[1], a[2], a[3]], target_qubit=a[4])
    
    # Apply phase
    qc.z(a[4])
    
    # Uncompute AND
    qc.mcx(control_qubits=[a[0], a[1], a[2], a[3]], target_qubit=a[4])
    
    # Uncompute clause 4
    qc.x(a[3])
    qc.ccx(p[0], p[1], a[4])
    qc.ccx(a[4], p[2], a[3])
    qc.ccx(p[0], p[1], a[4])
    
    # Uncompute clause 3
    qc.x(a[2])
    qc.x(p[1])
    qc.x(p[2])
    qc.ccx(p[0], p[1], a[4])
    qc.ccx(a[4], p[2], a[2])
    qc.ccx(p[0], p[1], a[4])
    qc.x(p[2])
    qc.x(p[1])
    
    # Uncompute clause 2
    qc.x(a[1])
    qc.x(p[2])
    qc.ccx(p[0], p[1], a[4])
    qc.ccx(a[4], p[2], a[1])
    qc.ccx(p[0], p[1], a[4])
    qc.x(p[2])
    
    # Uncompute clause 1
    qc.x(a[0])
    qc.x(p[0])
    qc.ccx(p[0], p[1], a[4])
    qc.ccx(a[4], p[2], a[0])
    qc.ccx(p[0], p[1], a[4])
    qc.x(p[0])
