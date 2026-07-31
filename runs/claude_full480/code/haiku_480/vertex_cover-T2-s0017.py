def build_oracle(qc, problem_qubits, ancilla_qubits):
    q0, q1, q2, q3, q4 = problem_qubits[0:5]
    
    # Ancilla allocation
    a_xor23 = ancilla_qubits[0]   # q2 XOR q3
    a_notq0 = ancilla_qubits[1]   # NOT q0
    a_notq4 = ancilla_qubits[2]   # NOT q4
    a_temp1 = ancilla_qubits[3]   # a_notq0 AND q1
    a_temp2 = ancilla_qubits[4]   # a_notq4 AND a_xor23
    a_result = ancilla_qubits[5]  # a_temp1 AND a_temp2
    
    # Compute: q2 XOR q3
    qc.cx(q2, a_xor23)
    qc.cx(q3, a_xor23)
    
    # Compute: NOT q0
    qc.x(a_notq0)
    qc.cx(q0, a_notq0)
    
    # Compute: NOT q4
    qc.x(a_notq4)
    qc.cx(q4, a_notq4)
    
    # Compute: a_notq0 AND q1
    qc.ccx(a_notq0, q1, a_temp1)
    
    # Compute: a_notq4 AND a_xor23
    qc.ccx(a_notq4, a_xor23, a_temp2)
    
    # Compute: a_temp1 AND a_temp2
    qc.ccx(a_temp1, a_temp2, a_result)
    
    # Phase: apply -1 if condition met
    qc.z(a_result)
    
    # Uncompute (reverse order)
    qc.ccx(a_temp1, a_temp2, a_result)
    qc.ccx(a_notq4, a_xor23, a_temp2)
    qc.ccx(a_notq0, q1, a_temp1)
    qc.cx(q4, a_notq4)
    qc.x(a_notq4)
    qc.cx(q0, a_notq0)
    qc.x(a_notq0)
    qc.cx(q3, a_xor23)
    qc.cx(q2, a_xor23)
