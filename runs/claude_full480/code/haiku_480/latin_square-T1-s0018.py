def build_oracle(qc, problem_qubits, ancilla_qubits):
    x0, x1, x2, x3 = problem_qubits[0:4]
    a0, a1, a2 = ancilla_qubits[0:3]
    
    # Compute x0 XNOR x1 into a0
    # (free cell 0 must decode to value 0, which means code 0 or 3)
    qc.cx(x0, a0)
    qc.cx(x1, a0)
    qc.x(a0)
    
    # Compute x2 AND NOT x3 into a1
    # (free cell 1 must decode to value 1, which means code 1)
    qc.x(x3)
    qc.ccx(x2, x3, a1)
    qc.x(x3)
    
    # Compute a0 AND a1 into a2
    qc.ccx(a0, a1, a2)
    
    # Apply Z gate for phase
    qc.z(a2)
    
    # Uncompute
    qc.ccx(a0, a1, a2)
    qc.x(x3)
    qc.ccx(x2, x3, a1)
    qc.x(x3)
    qc.x(a0)
    qc.cx(x1, a0)
    qc.cx(x0, a0)
