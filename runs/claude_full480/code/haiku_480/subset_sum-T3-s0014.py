def build_oracle(qc, problem_qubits, ancilla_qubits):
    flag = ancilla_qubits[0]
    
    # Only subset [6] sums to target T=6, corresponding to state |10000>
    # (i.e., only element a[0]=6 is selected)
    # Mark this state with a -1 phase
    
    # Step 1: Flip bits 1-4 to negate them
    qc.x(problem_qubits[1])
    qc.x(problem_qubits[2])
    qc.x(problem_qubits[3])
    qc.x(problem_qubits[4])
    
    # Step 2: Compute flag = AND of all 5 problem qubits
    # After flipping, all 5 bits are 1 iff we're in the target state |10000>
    qc.mcx(problem_qubits, flag)
    
    # Step 3: Apply phase -1 via Z gate on flag
    qc.z(flag)
    
    # Step 4: Uncompute flag back to 0
    qc.mcx(problem_qubits, flag)
    
    # Step 5: Flip bits 1-4 back to restore original state
    qc.x(problem_qubits[1])
    qc.x(problem_qubits[2])
    qc.x(problem_qubits[3])
    qc.x(problem_qubits[4])
