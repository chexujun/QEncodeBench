def build_oracle(qc, problem_qubits, ancilla_qubits):
    q = problem_qubits
    a = ancilla_qubits
    
    # COMPUTE: Verify each free cell has value 0 (code 00 or 11)
    # Cell 0 has value 0 iff q[0] == q[1], computed as XOR = 0
    qc.cx(q[0], a[0])
    qc.cx(q[1], a[0])  # a[0] = q[0] XOR q[1]
    
    # Cell 1 has value 0 iff q[2] == q[3], computed as XOR = 0
    qc.cx(q[2], a[1])
    qc.cx(q[3], a[1])  # a[1] = q[2] XOR q[3]
    
    # COMPUTE: Both cells must be 0 for valid Latin square
    # Initialize control qubit to 1, flip it if either XOR is 1
    qc.x(a[2])  # a[2] = 1
    qc.cx(a[0], a[2])  # flip a[2] if a[0] == 1
    qc.cx(a[1], a[2])  # flip a[2] if a[1] == 1
    # Now a[2] = 1 iff both a[0] = 0 and a[1] = 0
    
    # PHASE: Apply -1 when both constraints are satisfied
    qc.z(a[2])
    
    # UNCOMPUTE: Reverse the control computation
    qc.cx(a[1], a[2])
    qc.cx(a[0], a[2])
    qc.x(a[2])
    
    # UNCOMPUTE: Reverse the XOR computations
    qc.cx(q[3], a[1])
    qc.cx(q[2], a[1])
    
    qc.cx(q[1], a[0])
    qc.cx(q[0], a[0])
