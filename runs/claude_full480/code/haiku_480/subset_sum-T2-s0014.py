def build_oracle(qc, problem_qubits, ancilla_qubits):
    q0, q1, q2, q3 = problem_qubits
    a0, a1, a2, a3 = ancilla_qubits[:4]
    
    # Compute NOT x_i into ancillas for i = 1,2,3
    qc.x(a1)
    qc.cx(q1, a1)
    
    qc.x(a2)
    qc.cx(q2, a2)
    
    qc.x(a3)
    qc.cx(q3, a3)
    
    # Compute AND into a0: a0 = q0 AND a1 AND a2 AND a3
    qc.mcx([q0, a1, a2, a3], a0)
    
    # Apply phase flip
    qc.z(a0)
    
    # Uncompute
    qc.mcx([q0, a1, a2, a3], a0)
    
    qc.cx(q3, a3)
    qc.x(a3)
    
    qc.cx(q2, a2)
    qc.x(a2)
    
    qc.cx(q1, a1)
    qc.x(a1)
