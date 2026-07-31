def build_oracle(qc, problem_qubits, ancilla_qubits):
    p0, p1, p2, p3 = problem_qubits
    a0, a1, a2, a3 = ancilla_qubits[:4]
    
    # Compute a0 = p0 XOR p1
    qc.cx(p0, a0)
    qc.cx(p1, a0)
    
    # Compute a1 = NOT p3
    qc.cx(p3, a1)  # a1 = p3
    qc.x(a1)       # a1 = NOT p3
    
    # Compute a2 = (NOT a0) AND p2
    # (NOT a0) is 1 when p0 == p1, which marks free cell 0 value as 0
    qc.x(a0)       # a0 = NOT(p0 XOR p1)
    qc.ccx(a0, p2, a2)  # a2 = a0 AND p2
    qc.x(a0)       # restore a0 = p0 XOR p1
    
    # Compute a3 = a2 AND a1
    # This marks valid states: (p0 == p1) AND (p2 == 1) AND (p3 == 0)
    qc.ccx(a2, a1, a3)
    
    # Apply phase
    qc.z(a3)
    
    # Uncompute a3
    qc.ccx(a2, a1, a3)
    
    # Uncompute a2
    qc.x(a0)
    qc.ccx(a0, p2, a2)
    qc.x(a0)
    
    # Uncompute a1
    qc.x(a1)
    qc.cx(p3, a1)
    
    # Uncompute a0
    qc.cx(p1, a0)
    qc.cx(p0, a0)
