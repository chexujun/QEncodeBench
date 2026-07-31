def build_oracle(qc, problem_qubits, ancilla_qubits):
    a0 = ancilla_qubits[0]
    
    # Flip qubit 4 to convert "must be 0" check to "must be 1"
    qc.x(problem_qubits[4])
    
    # Compute: multi-controlled X
    # a0 = 1 iff x[0]=1 AND x[1]=1 AND x[4]=1 (after flip) AND x[5]=1
    controls = [problem_qubits[0], problem_qubits[1], problem_qubits[4], problem_qubits[5]]
    qc.mcx(controls, a0)
    
    # Phase: apply Z gate (introduces -1 phase when a0 = |1>)
    qc.z(a0)
    
    # Uncompute: reverse multi-controlled X to restore a0 to |0>
    qc.mcx(controls, a0)
    
    # Restore qubit 4
    qc.x(problem_qubits[4])
