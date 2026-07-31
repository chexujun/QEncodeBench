def build_oracle(qc, problem_qubits, ancilla_qubits):
    a0, a1, a2, a3 = ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[2], ancilla_qubits[3]
    
    # Check offset 0: s[2]=0, s[3]=0, s[4]=1
    # Compute: NOT(s[2]) AND NOT(s[3]) AND s[4] into a0
    qc.x(problem_qubits[2])
    qc.x(problem_qubits[3])
    qc.mcx([problem_qubits[2], problem_qubits[3], problem_qubits[4]], a0)
    qc.x(problem_qubits[3])
    qc.x(problem_qubits[2])
    
    # Check offset 1: s[3]=0, s[4]=0, s[5]=1
    qc.x(problem_qubits[3])
    qc.x(problem_qubits[4])
    qc.mcx([problem_qubits[3], problem_qubits[4], problem_qubits[5]], a1)
    qc.x(problem_qubits[4])
    qc.x(problem_qubits[3])
    
    # Check offset 2: s[4]=0, s[5]=0, s[6]=1
    qc.x(problem_qubits[4])
    qc.x(problem_qubits[5])
    qc.mcx([problem_qubits[4], problem_qubits[5], problem_qubits[6]], a2)
    qc.x(problem_qubits[5])
    qc.x(problem_qubits[4])
    
    # Compute OR(a0, a1, a2) = NOT(NOT(a0) AND NOT(a1) AND NOT(a2)) into a3
    qc.x(a0)
    qc.x(a1)
    qc.x(a2)
    qc.mcx([a0, a1, a2], a3)
    qc.x(a2)
    qc.x(a1)
    qc.x(a0)
    qc.x(a3)  # Final flip to get OR result
    
    # Apply phase -1 iff a3=1 (pattern matches)
    qc.z(a3)
    
    # Uncompute OR
    qc.x(a3)
    qc.x(a0)
    qc.x(a1)
    qc.x(a2)
    qc.mcx([a0, a1, a2], a3)
    qc.x(a2)
    qc.x(a1)
    qc.x(a0)
    
    # Uncompute offset 2
    qc.x(problem_qubits[4])
    qc.x(problem_qubits[5])
    qc.mcx([problem_qubits[4], problem_qubits[5], problem_qubits[6]], a2)
    qc.x(problem_qubits[5])
    qc.x(problem_qubits[4])
    
    # Uncompute offset 1
    qc.x(problem_qubits[3])
    qc.x(problem_qubits[4])
    qc.mcx([problem_qubits[3], problem_qubits[4], problem_qubits[5]], a1)
    qc.x(problem_qubits[4])
    qc.x(problem_qubits[3])
    
    # Uncompute offset 0
    qc.x(problem_qubits[2])
    qc.x(problem_qubits[3])
    qc.mcx([problem_qubits[2], problem_qubits[3], problem_qubits[4]], a0)
    qc.x(problem_qubits[3])
    qc.x(problem_qubits[2])
