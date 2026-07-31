def build_oracle(qc, problem_qubits, ancilla_qubits):
    a0 = ancilla_qubits[0]
    
    # Flip bit 5 to convert pattern |111110> to |111111> (all 1s)
    qc.x(problem_qubits[5])
    
    # Compute AND of all problem qubits into ancilla
    # Ancilla becomes |1> iff all problem qubits are |1>
    qc.mcx(problem_qubits, a0)
    
    # Apply phase -1 if ancilla is |1>
    qc.z(a0)
    
    # Uncompute: restore ancilla to |0>
    qc.mcx(problem_qubits, a0)
    
    # Undo the flip of bit 5
    qc.x(problem_qubits[5])
