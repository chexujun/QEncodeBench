def build_oracle(qc, problem_qubits, ancilla_qubits):
    a0, a1, a2, a_final = ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[2], ancilla_qubits[3]
    
    # COMPUTE PHASE: Compute each offset match into ancillas
    
    # Offset 0 match: s[0]=1 AND s[2]=0 AND s[3]=1 AND s[4]=0
    qc.x(problem_qubits[2])
    qc.x(problem_qubits[4])
    qc.mcx([problem_qubits[0], problem_qubits[2], problem_qubits[3], problem_qubits[4]], a0)
    qc.x(problem_qubits[2])
    qc.x(problem_qubits[4])
    
    # Offset 1 match: s[1]=1 AND s[3]=0 AND s[4]=1 AND s[5]=0
    qc.x(problem_qubits[3])
    qc.x(problem_qubits[5])
    qc.mcx([problem_qubits[1], problem_qubits[3], problem_qubits[4], problem_qubits[5]], a1)
    qc.x(problem_qubits[3])
    qc.x(problem_qubits[5])
    
    # Offset 2 match: s[2]=1 AND s[4]=0 AND s[5]=1 AND s[6]=0
    qc.x(problem_qubits[4])
    qc.x(problem_qubits[6])
    qc.mcx([problem_qubits[2], problem_qubits[4], problem_qubits[5], problem_qubits[6]], a2)
    qc.x(problem_qubits[4])
    qc.x(problem_qubits[6])
    
    # Compute OR of all matches: a_final = a0 OR a1 OR a2
    qc.x(a0)
    qc.x(a1)
    qc.x(a2)
    qc.mcx([a0, a1, a2], a_final)
    qc.x(a0)
    qc.x(a1)
    qc.x(a2)
    qc.x(a_final)
    
    # APPLY PHASE: Mark states where pattern matches
    qc.z(a_final)
    
    # UNCOMPUTE PHASE: Reverse all operations in reverse order
    
    # Uncompute OR of all matches
    qc.x(a_final)
    qc.x(a0)
    qc.x(a1)
    qc.x(a2)
    qc.mcx([a0, a1, a2], a_final)
    qc.x(a0)
    qc.x(a1)
    qc.x(a2)
    
    # Uncompute offset 2 match
    qc.x(problem_qubits[4])
    qc.x(problem_qubits[6])
    qc.mcx([problem_qubits[2], problem_qubits[4], problem_qubits[5], problem_qubits[6]], a2)
    qc.x(problem_qubits[4])
    qc.x(problem_qubits[6])
    
    # Uncompute offset 1 match
    qc.x(problem_qubits[3])
    qc.x(problem_qubits[5])
    qc.mcx([problem_qubits[1], problem_qubits[3], problem_qubits[4], problem_qubits[5]], a1)
    qc.x(problem_qubits[3])
    qc.x(problem_qubits[5])
    
    # Uncompute offset 0 match
    qc.x(problem_qubits[2])
    qc.x(problem_qubits[4])
    qc.mcx([problem_qubits[0], problem_qubits[2], problem_qubits[3], problem_qubits[4]], a0)
    qc.x(problem_qubits[2])
    qc.x(problem_qubits[4])
