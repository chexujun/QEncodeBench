def build_oracle(qc, problem_qubits, ancilla_qubits):
    p = problem_qubits
    a = ancilla_qubits
    
    flag = a[0]
    inv_p1 = a[1]
    inv_p2 = a[2]
    inv_p3 = a[3]
    
    # Compute: inv_p[i] = NOT(p[i])
    qc.x(inv_p1)
    qc.cx(p[1], inv_p1)
    
    qc.x(inv_p2)
    qc.cx(p[2], inv_p2)
    
    qc.x(inv_p3)
    qc.cx(p[3], inv_p3)
    
    # Compute: flag = p[0] AND NOT(p[1]) AND NOT(p[2]) AND NOT(p[3])
    qc.mcx([p[0], inv_p1, inv_p2, inv_p3], flag)
    
    # Apply phase: -1 iff flag = 1 (which occurs only for |0001>)
    qc.z(flag)
    
    # Uncompute flag
    qc.mcx([p[0], inv_p1, inv_p2, inv_p3], flag)
    
    # Uncompute inverses
    qc.cx(p[3], inv_p3)
    qc.x(inv_p3)
    
    qc.cx(p[2], inv_p2)
    qc.x(inv_p2)
    
    qc.cx(p[1], inv_p1)
    qc.x(inv_p1)
