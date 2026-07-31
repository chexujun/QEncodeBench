def build_oracle(qc, problem_qubits, ancilla_qubits):
    s = problem_qubits
    a0, a1, a2 = ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[2]
    
    # Compute match0 = (NOT s[0]) AND (NOT s[1]) AND s[2] AND (NOT s[3]) AND s[5]
    qc.x(s[0])
    qc.x(s[1])
    qc.x(s[3])
    
    qc.mcx([s[0], s[1], s[2], s[3], s[5]], a0)
    
    qc.x(s[0])
    qc.x(s[1])
    qc.x(s[3])
    
    # Compute match1 = (NOT s[1]) AND (NOT s[2]) AND s[3] AND (NOT s[4]) AND s[6]
    qc.x(s[1])
    qc.x(s[2])
    qc.x(s[4])
    
    qc.mcx([s[1], s[2], s[3], s[4], s[6]], a1)
    
    qc.x(s[1])
    qc.x(s[2])
    qc.x(s[4])
    
    # Compute match0 OR match1 into a2
    qc.x(a0)
    qc.x(a1)
    
    qc.mcx([a0, a1], a2)  # a2 = (NOT match0) AND (NOT match1)
    
    qc.x(a0)
    qc.x(a1)
    qc.x(a2)  # a2 = match0 OR match1
    
    # Apply phase -1
    qc.z(a2)
    
    # Uncompute match0 OR match1
    qc.x(a2)
    
    qc.x(a0)
    qc.x(a1)
    qc.mcx([a0, a1], a2)
    qc.x(a1)
    qc.x(a0)
    
    # Uncompute match1
    qc.x(s[1])
    qc.x(s[2])
    qc.x(s[4])
    
    qc.mcx([s[1], s[2], s[3], s[4], s[6]], a1)
    
    qc.x(s[1])
    qc.x(s[2])
    qc.x(s[4])
    
    # Uncompute match0
    qc.x(s[0])
    qc.x(s[1])
    qc.x(s[3])
    
    qc.mcx([s[0], s[1], s[2], s[3], s[5]], a0)
    
    qc.x(s[0])
    qc.x(s[1])
    qc.x(s[3])
