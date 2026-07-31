def build_oracle(qc, problem_qubits, ancilla_qubits):
    # Extract problem qubits
    b0_0, b1_0 = problem_qubits[0], problem_qubits[1]  # cell (0,0)
    b0_2, b1_2 = problem_qubits[2], problem_qubits[3]  # cell (2,2)
    
    # Extract ancilla qubits (need 5 total)
    a0, a1, a2, a3, a4 = ancilla_qubits[0:5]
    
    # COMPUTE
    # Compute b0_0 XOR b1_0 into a0
    qc.cx(b0_0, a0)
    qc.cx(b1_0, a0)
    
    # Compute NOT b0_2 into a1
    qc.x(b0_2)
    qc.cx(b0_2, a1)
    qc.x(b0_2)
    
    # Copy b1_2 to a2
    qc.cx(b1_2, a2)
    
    # Negate a0 to get NOT(b0_0 XOR b1_0), i.e., b0_0 == b1_0
    qc.x(a0)
    
    # Compute a0 AND a1 into a3
    qc.ccx(a0, a1, a3)
    
    # Compute a3 AND a2 into a4 (final condition: all three predicates true)
    qc.ccx(a3, a2, a4)
    
    # PHASE
    qc.z(a4)
    
    # UNCOMPUTE (reverse order)
    qc.ccx(a3, a2, a4)
    qc.ccx(a0, a1, a3)
    qc.x(a0)
    qc.cx(b1_2, a2)
    qc.x(b0_2)
    qc.cx(b0_2, a1)
    qc.x(b0_2)
    qc.cx(b1_0, a0)
    qc.cx(b0_0, a0)
