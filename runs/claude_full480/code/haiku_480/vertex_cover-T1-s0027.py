def build_oracle(qc, problem_qubits, ancilla_qubits):
    x = problem_qubits
    a = ancilla_qubits
    
    # Compute AND terms
    qc.ccx(x[1], x[2], a[0])
    qc.ccx(x[1], x[3], a[1])
    qc.ccx(x[2], x[3], a[2])
    
    # Compute oracle flag: x[0] AND NOT(a[0]) AND NOT(a[1]) AND NOT(a[2])
    qc.x(a[0])
    qc.x(a[1])
    qc.x(a[2])
    qc.mcx([x[0], a[0], a[1], a[2]], a[3])
    qc.x(a[0])
    qc.x(a[1])
    qc.x(a[2])
    
    # Apply phase flip
    qc.z(a[3])
    
    # Uncompute
    qc.x(a[0])
    qc.x(a[1])
    qc.x(a[2])
    qc.mcx([x[0], a[0], a[1], a[2]], a[3])
    qc.x(a[0])
    qc.x(a[1])
    qc.x(a[2])
    
    qc.ccx(x[2], x[3], a[2])
    qc.ccx(x[1], x[3], a[1])
    qc.ccx(x[1], x[2], a[0])
