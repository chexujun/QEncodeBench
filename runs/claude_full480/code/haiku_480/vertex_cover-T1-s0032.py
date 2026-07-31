def build_oracle(qc, problem_qubits, ancilla_qubits):
    x0, x1, x2, x3 = problem_qubits[0], problem_qubits[1], problem_qubits[2], problem_qubits[3]
    a0, a1, a2, a3, a4, a5 = ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[2], ancilla_qubits[3], ancilla_qubits[4], ancilla_qubits[5]
    
    # COMPUTE phase
    
    # Condition 1: {0,2} = x0 AND NOT x1 AND x2 AND NOT x3 -> a0
    qc.x(x1)
    qc.x(x3)
    qc.mcx([x0, x1, x2, x3], a0)
    qc.x(x3)
    qc.x(x1)
    
    # Condition 2: {1,3} = NOT x0 AND x1 AND NOT x2 AND x3 -> a1
    qc.x(x0)
    qc.x(x2)
    qc.mcx([x0, x1, x2, x3], a1)
    qc.x(x2)
    qc.x(x0)
    
    # Condition 3: {2,3} = NOT x0 AND NOT x1 AND x2 AND x3 -> a2
    qc.x(x0)
    qc.x(x1)
    qc.mcx([x0, x1, x2, x3], a2)
    qc.x(x1)
    qc.x(x0)
    
    # Compute a0 OR a1 -> a4 (using a5 as temp; a5 = a0 AND a1)
    qc.cx(a0, a4)
    qc.cx(a1, a4)
    qc.ccx(a0, a1, a5)
    qc.cx(a5, a4)
    
    # Compute a4 OR a2 -> a3 (using a5 as temp; a5 = a4 AND a2)
    qc.cx(a4, a3)
    qc.cx(a2, a3)
    qc.ccx(a4, a2, a5)
    qc.cx(a5, a3)
    
    # PHASE
    qc.z(a3)
    
    # UNCOMPUTE phase (reverse order)
    
    # Undo (a4 OR a2) -> a3
    qc.cx(a5, a3)
    qc.ccx(a4, a2, a5)
    qc.cx(a2, a3)
    qc.cx(a4, a3)
    
    # Recompute a5 = a0 AND a1 for next undo
    qc.ccx(a0, a1, a5)
    
    # Undo (a0 OR a1) -> a4
    qc.cx(a5, a4)
    qc.ccx(a0, a1, a5)
    qc.cx(a1, a4)
    qc.cx(a0, a4)
    
    # Undo Condition 3
    qc.x(x0)
    qc.x(x1)
    qc.mcx([x0, x1, x2, x3], a2)
    qc.x(x1)
    qc.x(x0)
    
    # Undo Condition 2
    qc.x(x0)
    qc.x(x2)
    qc.mcx([x0, x1, x2, x3], a1)
    qc.x(x2)
    qc.x(x0)
    
    # Undo Condition 1
    qc.x(x1)
    qc.x(x3)
    qc.mcx([x0, x1, x2, x3], a0)
    qc.x(x3)
    qc.x(x1)
