def build_oracle(qc, problem_qubits, ancilla_qubits):
    q0, q1, q2, q3 = problem_qubits[0:4]
    a0, a1, a2 = ancilla_qubits[0:3]
    
    # Identify valid vertex covers of size ≤ 2:
    # Graph edges: (0,1), (1,2), (1,3), (2,3)
    # Valid covers: {1,2} → x=0110 (q0=0,q1=1,q2=1,q3=0)
    #               {1,3} → x=1010 (q0=0,q1=1,q2=0,q3=1)
    # Simplified predicate: f(x) = q1 AND (NOT q0) AND (q2 XOR q3)
    
    # Compute q2 XOR q3 into a0
    qc.cx(q2, a0)
    qc.cx(q3, a0)
    
    # Compute (NOT q0) AND a0 into a1
    qc.x(q0)
    qc.ccx(q0, a0, a1)
    qc.x(q0)
    
    # Compute a1 AND q1 into a2
    qc.ccx(a1, q1, a2)
    
    # Apply phase -1 when f(x) = 1
    qc.z(a2)
    
    # Uncompute in reverse order
    qc.ccx(a1, q1, a2)
    qc.x(q0)
    qc.ccx(q0, a0, a1)
    qc.x(q0)
    qc.cx(q3, a0)
    qc.cx(q2, a0)
