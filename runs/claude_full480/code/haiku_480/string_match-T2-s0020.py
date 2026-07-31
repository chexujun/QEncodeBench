def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a0 = ancilla_qubits[0]
    a1 = ancilla_qubits[1]
    temp = ancilla_qubits[2]
    
    # Compute condition 0: s[0]=1, s[1]=0, s[2]=1, s[3]=0, s[4]=1, s[5]=0
    qc.x(problem_qubits[1])
    qc.x(problem_qubits[3])
    qc.x(problem_qubits[5])
    qc.mcx([problem_qubits[0], problem_qubits[1], problem_qubits[2],
            problem_qubits[3], problem_qubits[4], problem_qubits[5]], a0)
    qc.x(problem_qubits[5])
    qc.x(problem_qubits[3])
    qc.x(problem_qubits[1])
    
    # Compute condition 1: s[1]=1, s[2]=0, s[3]=1, s[4]=0, s[5]=1, s[6]=0
    qc.x(problem_qubits[2])
    qc.x(problem_qubits[4])
    qc.x(problem_qubits[6])
    qc.mcx([problem_qubits[1], problem_qubits[2], problem_qubits[3],
            problem_qubits[4], problem_qubits[5], problem_qubits[6]], a1)
    qc.x(problem_qubits[6])
    qc.x(problem_qubits[4])
    qc.x(problem_qubits[2])
    
    # Compute a0 OR a1 into temp via De Morgan's law: a0|a1 = NOT(NOT a0 AND NOT a1)
    qc.x(a0)
    qc.x(a1)
    qc.mcx([a0, a1], temp)
    qc.x(temp)
    
    # Apply phase -1 to states where pattern matches
    qc.z(temp)
    
    # Uncompute a0 OR a1
    qc.x(temp)
    qc.mcx([a0, a1], temp)
    qc.x(a1)
    qc.x(a0)
    
    # Uncompute condition 1
    qc.x(problem_qubits[2])
    qc.x(problem_qubits[4])
    qc.x(problem_qubits[6])
    qc.mcx([problem_qubits[1], problem_qubits[2], problem_qubits[3],
            problem_qubits[4], problem_qubits[5], problem_qubits[6]], a1)
    qc.x(problem_qubits[6])
    qc.x(problem_qubits[4])
    qc.x(problem_qubits[2])
    
    # Uncompute condition 0
    qc.x(problem_qubits[1])
    qc.x(problem_qubits[3])
    qc.x(problem_qubits[5])
    qc.mcx([problem_qubits[0], problem_qubits[1], problem_qubits[2],
            problem_qubits[3], problem_qubits[4], problem_qubits[5]], a0)
    qc.x(problem_qubits[5])
    qc.x(problem_qubits[3])
    qc.x(problem_qubits[1])
