def build_oracle(qc, problem_qubits, ancilla_qubits):
    q = problem_qubits  # q[0..4]
    a = ancilla_qubits  # a[0..2]
    
    # Compute offset 0: text[0:4] matches "1101" -> q[0]=1, q[1]=1, q[2]=0, q[3]=1
    qc.ccx(q[0], q[1], a[0])
    qc.x(q[2])
    qc.ccx(q[2], a[0], a[0])
    qc.x(q[2])
    qc.x(q[3])
    qc.ccx(q[3], a[0], a[0])
    qc.x(q[3])
    
    # Compute offset 1: text[1:5] matches "1101" -> q[1]=1, q[2]=1, q[3]=0, q[4]=1
    qc.ccx(q[1], q[2], a[1])
    qc.x(q[3])
    qc.ccx(q[3], a[1], a[1])
    qc.x(q[3])
    qc.x(q[4])
    qc.ccx(q[4], a[1], a[1])
    qc.x(q[4])
    
    # Compute a[0] OR a[1] into a[2]
    qc.cx(a[0], a[2])
    qc.cx(a[1], a[2])
    qc.ccx(a[0], a[1], a[2])
    
    # Apply phase -1 if either offset matches
    qc.z(a[2])
    
    # Uncompute a[2]
    qc.ccx(a[0], a[1], a[2])
    qc.cx(a[1], a[2])
    qc.cx(a[0], a[2])
    
    # Uncompute a[1]
    qc.x(q[4])
    qc.ccx(q[4], a[1], a[1])
    qc.x(q[4])
    qc.x(q[3])
    qc.ccx(q[3], a[1], a[1])
    qc.x(q[3])
    qc.ccx(q[1], q[2], a[1])
    
    # Uncompute a[0]
    qc.x(q[3])
    qc.ccx(q[3], a[0], a[0])
    qc.x(q[3])
    qc.x(q[2])
    qc.ccx(q[2], a[0], a[0])
    qc.x(q[2])
    qc.ccx(q[0], q[1], a[0])
