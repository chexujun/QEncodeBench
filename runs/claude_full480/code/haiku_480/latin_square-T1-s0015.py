def build_oracle(qc, problem_qubits, ancilla_qubits):
    q0, q1, q2, q3 = problem_qubits[:4]
    a0, a1, a2, a3, a_temp_xor, a_or_state, result = ancilla_qubits[:7]
    
    # Compute individual bits
    # a0 = NOT q0, a1 = q1, a2 = q2, a3 = q3
    qc.x(a0)
    qc.cx(q0, a0)
    
    qc.cx(q1, a1)
    qc.cx(q2, a2)
    qc.cx(q3, a3)
    
    # Compute a_temp_xor = q2 XOR q3
    qc.cx(a2, a_temp_xor)
    qc.cx(a3, a_temp_xor)
    
    # Compute a_or_state = NOT(q2 XOR q3) = q2 XNOR q3
    qc.x(a_or_state)
    qc.cx(a_temp_xor, a_or_state)
    
    # Compute result = (NOT q0) AND q1 AND (q2 XNOR q3)
    qc.x(result)
    for a in [a0, a1, a_or_state]:
        qc.x(a)
        qc.cx(a, result)
        qc.x(a)
    
    # Apply phase -1
    qc.z(result)
    
    # Uncompute result
    for a in reversed([a0, a1, a_or_state]):
        qc.x(a)
        qc.cx(a, result)
        qc.x(a)
    qc.x(result)
    
    # Uncompute a_or_state
    qc.cx(a_temp_xor, a_or_state)
    qc.x(a_or_state)
    
    # Uncompute a_temp_xor
    qc.cx(a3, a_temp_xor)
    qc.cx(a2, a_temp_xor)
    
    # Uncompute a0, a1, a2, a3
    qc.cx(q3, a3)
    qc.cx(q2, a2)
    qc.cx(q1, a1)
    qc.cx(q0, a0)
    qc.x(a0)
