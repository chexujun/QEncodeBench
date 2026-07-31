def build_oracle(qc, problem_qubits, ancilla_qubits):
    q = problem_qubits
    a = ancilla_qubits
    
    # Compute c0: v0 = 0 (value is 0 or 3, i.e., NOT(q0 XOR q1))
    qc.cx(q[0], a[0])
    qc.cx(q[1], a[0])
    qc.x(a[0])
    
    # Compute c1: v1 = 1 (q2 = 1 AND q3 = 0)
    qc.x(q[3])
    qc.ccx(q[2], q[3], a[1])
    qc.x(q[3])
    
    # Compute c2: v2 = 0 (NOT(q4 XOR q5))
    qc.cx(q[4], a[2])
    qc.cx(q[5], a[2])
    qc.x(a[2])
    
    # Compute c3: v3 = 1 (q6 = 1 AND q7 = 0)
    qc.x(q[7])
    qc.ccx(q[6], q[7], a[3])
    qc.x(q[7])
    
    # Compute AND(c0, c1) into a[4]
    qc.ccx(a[0], a[1], a[4])
    
    # Compute AND(c2, c3) into a[5]
    qc.ccx(a[2], a[3], a[5])
    
    # Clear a[3] by uncomputing c3
    qc.x(q[7])
    qc.ccx(q[6], q[7], a[3])
    qc.x(q[7])
    
    # Compute AND(a[4], a[5]) into a[3]
    qc.ccx(a[4], a[5], a[3])
    
    # Apply phase
    qc.z(a[3])
    
    # Uncompute AND(a[4], a[5])
    qc.ccx(a[4], a[5], a[3])
    
    # Recompute c3 into a[3] for uncompute steps
    qc.x(q[7])
    qc.ccx(q[6], q[7], a[3])
    qc.x(q[7])
    
    # Uncompute AND(c2, c3)
    qc.ccx(a[2], a[3], a[5])
    
    # Uncompute c2
    qc.x(a[2])
    qc.cx(q[5], a[2])
    qc.cx(q[4], a[2])
    
    # Uncompute c3
    qc.x(q[7])
    qc.ccx(q[6], q[7], a[3])
    qc.x(q[7])
    
    # Uncompute AND(c0, c1)
    qc.ccx(a[0], a[1], a[4])
    
    # Uncompute c0
    qc.x(a[0])
    qc.cx(q[1], a[0])
    qc.cx(q[0], a[0])
    
    # Uncompute c1
    qc.x(q[3])
    qc.ccx(q[2], q[3], a[1])
    qc.x(q[3])
