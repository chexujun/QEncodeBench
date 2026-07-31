def build_oracle(qc, problem_qubits, ancilla_qubits):
    a0 = ancilla_qubits[0]
    a1 = ancilla_qubits[1]
    
    # Pattern "?0?100": match iff s_1==0 AND s_3==1 AND s_4==0 AND s_5==0
    
    # COMPUTE: Transform bits so all conditions become "qubit is 1"
    qc.x(problem_qubits[1])
    qc.x(problem_qubits[4])
    qc.x(problem_qubits[5])
    
    # Compute: a0 = (NOT s_1) AND s_3 AND (NOT s_4) AND (NOT s_5)
    controls = [problem_qubits[1], problem_qubits[3], problem_qubits[4], problem_qubits[5]]
    qc.mcx(controls, a0, [a1])
    
    # PHASE: Apply -1 phase to marked states
    qc.z(a0)
    
    # UNCOMPUTE:
    qc.mcx(controls, a0, [a1])
    
    # Restore bits
    qc.x(problem_qubits[5])
    qc.x(problem_qubits[4])
    qc.x(problem_qubits[1])
