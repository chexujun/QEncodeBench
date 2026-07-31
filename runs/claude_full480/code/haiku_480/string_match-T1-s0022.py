def build_oracle(qc, problem_qubits, ancilla_qubits):
    q0, q1, q2, q3, q4 = problem_qubits
    a0, a1 = ancilla_qubits
    
    # Pattern: "0001?"
    # f(x) = 1 iff (q0==0) AND (q1==0) AND (q2==0) AND (q3==1)
    
    # Flip q0, q1, q2 to convert the condition
    qc.x(q0)
    qc.x(q1)
    qc.x(q2)
    
    # Check if all four conditions are met using multi-controlled X
    qc.mcx([q0, q1, q2, q3], a0, ancilla_qubits=[a1])
    
    # Apply phase -1 if condition is met
    qc.z(a0)
    
    # Uncompute the ancilla
    qc.mcx([q0, q1, q2, q3], a0, ancilla_qubits=[a1])
    
    # Flip q0, q1, q2 back
    qc.x(q2)
    qc.x(q1)
    qc.x(q0)
