def build_oracle(qc, problem_qubits, ancilla_qubits):
    q0, q1, q2, q3 = problem_qubits[:4]
    a0, a1, a2, a3 = ancilla_qubits[:4]
    
    # Compute a0 = NOT(q0 XOR q1) = (q0 = q1)
    qc.x(a0)
    qc.cx(q0, a0)
    qc.cx(q1, a0)
    
    # Compute a1 = NOT q3
    qc.x(a1)
    qc.cx(q3, a1)
    
    # Compute a2 = a0 AND q2
    qc.ccx(a0, q2, a2)
    
    # Compute a3 = a2 AND a1
    qc.ccx(a2, a1, a3)
    
    # Apply phase
    qc.z(a3)
    
    # Uncompute
    qc.ccx(a2, a1, a3)
    qc.ccx(a0, q2, a2)
    qc.cx(q3, a1)
    qc.x(a1)
    qc.cx(q1, a0)
    qc.cx(q0, a0)
    qc.x(a0)
