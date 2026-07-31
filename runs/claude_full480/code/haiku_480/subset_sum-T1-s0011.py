def build_oracle(qc, problem_qubits, ancilla_qubits):
    # Subset sum problem: a = [1, 5, 5], target = 10
    # Solution: select indices 1 and 2 (sum = 5 + 5 = 10)
    # Corresponds to: problem_qubits[0]=0, problem_qubits[1]=1, problem_qubits[2]=1
    # Predicate: (NOT x0) AND x1 AND x2
    
    # Ancilla allocation
    temp_not_x0 = ancilla_qubits[1]      # Stores NOT problem_qubits[0]
    result = ancilla_qubits[0]            # Stores final AND result
    temp_and = ancilla_qubits[2]          # Temporary for intermediate AND
    
    # Compute NOT problem_qubits[0] into temp_not_x0
    qc.x(temp_not_x0)                    # Initialize to |1⟩
    qc.cx(problem_qubits[0], temp_not_x0)  # temp_not_x0 = NOT problem_qubits[0]
    
    # Compute (NOT x0) AND x1 AND x2 into result
    qc.ccx(temp_not_x0, problem_qubits[1], temp_and)      # temp_and = (NOT x0) AND x1
    qc.ccx(temp_and, problem_qubits[2], result)           # result = ((NOT x0) AND x1) AND x2
    
    # Apply phase flip for marked states
    qc.z(result)
    
    # Uncompute to restore all ancillas to |0⟩
    qc.ccx(temp_and, problem_qubits[2], result)
    qc.ccx(temp_not_x0, problem_qubits[1], temp_and)
    qc.cx(problem_qubits[0], temp_not_x0)
    qc.x(temp_not_x0)
