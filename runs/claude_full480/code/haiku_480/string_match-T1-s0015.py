def build_oracle(qc, problem_qubits, ancilla_qubits):
    # Pattern is "01010"
    # Apply phase -1 to states matching the pattern
    
    # Compute: flip positions 0, 2, 4 (which should be 0)
    qc.x(problem_qubits[0])
    qc.x(problem_qubits[2])
    qc.x(problem_qubits[4])
    
    # Multi-controlled X: set ancilla[0] if all problem qubits are 1
    # (which happens iff the flipped pattern is all 1s, i.e., pattern matches)
    qc.mcx(problem_qubits, ancilla_qubits[0], ancilla_qubits[1])
    
    # Phase: apply Z to ancilla[0]
    qc.z(ancilla_qubits[0])
    
    # Uncompute: reverse the multi-controlled X
    qc.mcx(problem_qubits, ancilla_qubits[0], ancilla_qubits[1])
    
    # Unflip: restore problem qubits to original state
    qc.x(problem_qubits[0])
    qc.x(problem_qubits[2])
    qc.x(problem_qubits[4])
