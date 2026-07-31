def build_oracle(qc, problem_qubits, ancilla_qubits):
    q = problem_qubits
    a = ancilla_qubits
    
    # Compute constraint 1: q[0] XOR q[1]
    # After this, a[0] = 0 iff q[0] = q[1]
    qc.cx(q[0], a[0])
    qc.cx(q[1], a[0])
    
    # Prepare for multi-controlled check by flipping qubits
    # We need all conditions to be 1 to apply the phase:
    # - a[0] = 0 iff q[0] = q[1] → flip to make it 1 iff equal
    # - q[2] = 0 → flip to make it 1 iff it's 0
    # - q[3] = 1 → already correct
    # - q[4] = 1 → already correct
    # - q[5] = 0 → flip to make it 1 iff it's 0
    qc.x(a[0])
    qc.x(q[2])
    qc.x(q[5])
    
    # Compute AND of all constraints into a[1]
    qc.mcx([a[0], q[2], q[3], q[4], q[5]], a[1])
    
    # Apply phase flip if all constraints satisfied
    qc.z(a[1])
    
    # Uncompute the AND
    qc.mcx([a[0], q[2], q[3], q[4], q[5]], a[1])
    
    # Undo flips (reverse order)
    qc.x(q[5])
    qc.x(q[2])
    qc.x(a[0])
    
    # Uncompute constraint 1
    qc.cx(q[1], a[0])
    qc.cx(q[0], a[0])
