def build_oracle(qc, problem_qubits, ancilla_qubits):
    # Determine which states satisfy: vertex cover + size <= 2
    # Graph edges: (0,1), (0,2), (0,3), (1,2), (2,3)
    # Only valid vertex cover of size <= 2 is {0, 2}
    # This maps to x_0=1, x_1=0, x_2=1, x_3=0
    
    # Flip qubits that must be 0 in the target state
    qc.x(problem_qubits[1])
    qc.x(problem_qubits[3])
    
    # Now all problem_qubits must equal 1 for the target state
    # Compute AND(x_0, x_1, x_2, x_3) into ancilla using Toffoli chain
    temp1 = ancilla_qubits[0]
    temp2 = ancilla_qubits[1]
    result = ancilla_qubits[2]
    
    # Compute AND step-by-step with Toffoli gates
    qc.ccx(problem_qubits[0], problem_qubits[1], temp1)
    qc.ccx(temp1, problem_qubits[2], temp2)
    qc.ccx(temp2, problem_qubits[3], result)
    
    # Apply phase -1 when result qubit is 1
    qc.z(result)
    
    # Uncompute AND (reverse order of same gates)
    qc.ccx(temp2, problem_qubits[3], result)
    qc.ccx(temp1, problem_qubits[2], temp2)
    qc.ccx(problem_qubits[0], problem_qubits[1], temp1)
    
    # Restore the problem qubits we negated
    qc.x(problem_qubits[1])
    qc.x(problem_qubits[3])
