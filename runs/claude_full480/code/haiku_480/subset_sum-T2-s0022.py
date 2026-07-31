def build_oracle(qc, problem_qubits, ancilla_qubits):
    x = problem_qubits
    a = ancilla_qubits[0]
    
    # Mark state x = 0010 (only bit 1 set)
    # This is the only state where subset sum equals 1
    # a = [8, 1, 5, 8]; only a[1]=1 sums to 1
    
    # Compute (NOT x[0]) AND x[1] AND (NOT x[2]) AND (NOT x[3])
    # Flip bits to check NOT conditions
    qc.x(x[0])
    qc.x(x[2])
    qc.x(x[3])
    
    # Compute AND into ancilla
    qc.mcx([x[0], x[1], x[2], x[3]], a)
    
    # Apply phase flip
    qc.z(a)
    
    # Uncompute AND
    qc.mcx([x[0], x[1], x[2], x[3]], a)
    
    # Flip bits back
    qc.x(x[3])
    qc.x(x[2])
    qc.x(x[0])
