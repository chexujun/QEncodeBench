def build_oracle(qc, problem_qubits, ancilla_qubits):
    x0, x1, x2, x3, x4, x5 = problem_qubits
    a0, a1, a2, a3, a4, a5, a6 = ancilla_qubits
    
    # Initialize clause result ancillas to |1>
    qc.x(a0)
    qc.x(a1)
    qc.x(a2)
    qc.x(a3)
    qc.x(a4)
    qc.x(a5)
    
    # Clause 1: (NOT x0 OR NOT x1 OR x3) = NOT(x0 AND x1 AND NOT x3)
    qc.mcx([x0, x1, x3], a0, ctrl_state='0b011')
    
    # Clause 2: (NOT x2 OR x3 OR NOT x4) = NOT(x2 AND NOT x3 AND x4)
    qc.mcx([x2, x3, x4], a1, ctrl_state='0b101')
    
    # Clause 3: (x0 OR NOT x1 OR x2) = NOT(NOT x0 AND x1 AND NOT x2)
    qc.mcx([x0, x1, x2], a2, ctrl_state='0b010')
    
    # Clause 4: (x0 OR x2 OR x3) = NOT(NOT x0 AND NOT x2 AND NOT x3)
    qc.mcx([x0, x2, x3], a3, ctrl_state='0b000')
    
    # Clause 5: (NOT x0 OR NOT x2 OR x5) = NOT(x0 AND x2 AND NOT x5)
    qc.mcx([x0, x2, x5], a4, ctrl_state='0b011')
    
    # Clause 6: (NOT x1 OR NOT x2 OR x5) = NOT(x1 AND x2 AND NOT x5)
    qc.mcx([x1, x2, x5], a5, ctrl_state='0b011')
    
    # AND all clause results into a6
    qc.mcx([a0, a1, a2, a3, a4, a5], a6, ctrl_state='0b111111')
    
    # Apply phase: Z gate on a6 (phase -1 iff all clauses satisfied)
    qc.z(a6)
    
    # Uncompute: reverse all operations
    qc.mcx([a0, a1, a2, a3, a4, a5], a6, ctrl_state='0b111111')
    
    qc.mcx([x1, x2, x5], a5, ctrl_state='0b011')
    qc.x(a5)
    
    qc.mcx([x0, x2, x5], a4, ctrl_state='0b011')
    qc.x(a4)
    
    qc.mcx([x0, x2, x3], a3, ctrl_state='0b000')
    qc.x(a3)
    
    qc.mcx([x0, x1, x2], a2, ctrl_state='0b010')
    qc.x(a2)
    
    qc.mcx([x2, x3, x4], a1, ctrl_state='0b101')
    qc.x(a1)
    
    qc.mcx([x0, x1, x3], a0, ctrl_state='0b011')
    qc.x(a0)
