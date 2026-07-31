def build_oracle(qc, problem_qubits, ancilla_qubits):
    # Pattern is "10010"
    # Positions: 0='1', 1='0', 2='0', 3='1', 4='0'
    
    a0 = ancilla_qubits[0]
    p = problem_qubits
    
    # Flip qubits that need to be 0 in the pattern
    qc.x(p[1])  # Pattern position 1: '0'
    qc.x(p[2])  # Pattern position 2: '0'
    qc.x(p[4])  # Pattern position 4: '0'
    
    # Compute: a0 = AND(p[0], p[1], p[2], p[3], p[4])
    qc.mcx([p[0], p[1], p[2], p[3], p[4]], a0)
    
    # Apply phase: -1 if a0 = 1
    qc.z(a0)
    
    # Uncompute: a0 back to 0
    qc.mcx([p[0], p[1], p[2], p[3], p[4]], a0)
    
    # Unflip qubits
    qc.x(p[1])
    qc.x(p[2])
    qc.x(p[4])
