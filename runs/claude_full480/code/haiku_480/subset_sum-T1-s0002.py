def build_oracle(qc, problem_qubits, ancilla_qubits):
    q0, q1, q2 = problem_qubits
    a0, a1, a2 = ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[2]
    
    # Compute NOT q1 into a0
    qc.x(q1)
    qc.cx(q1, a0)
    qc.x(q1)
    
    # Compute q0 XOR q2 into a1
    qc.cx(q0, a1)
    qc.cx(q2, a1)
    
    # Compute AND: a0 AND a1 into a2
    qc.ccx(a0, a1, a2)
    
    # Apply phase -1 to marked states
    qc.z(a2)
    
    # Uncompute to restore ancillas to |0>
    qc.ccx(a0, a1, a2)
    qc.cx(q2, a1)
    qc.cx(q0, a1)
    qc.x(q1)
    qc.cx(q1, a0)
    qc.x(q1)
