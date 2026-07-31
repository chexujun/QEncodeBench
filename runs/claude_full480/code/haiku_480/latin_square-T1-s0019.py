def build_oracle(qc, problem_qubits, ancilla_qubits):
    # Latin square oracle: marks the unique valid completion
    # where both free cells (positions 0,0 and 2,2) must have value 2
    # Free cell 0: problem_qubits[0:2] must encode 2 (binary 10: b0=0, b1=1)
    # Free cell 1: problem_qubits[2:4] must encode 2 (binary 10: b0=0, b1=1)
    # Target state on problem qubits: |0101>
    
    q0, q1, q2, q3 = problem_qubits[0], problem_qubits[1], problem_qubits[2], problem_qubits[3]
    a0, a1, a2 = ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[2]
    
    # COMPUTE: Check if (q0=0) AND (q1=1) AND (q2=0) AND (q3=1)
    # Flip q0 and q2 to normalize checking to all 1s
    qc.x(q0)
    qc.x(q2)
    
    # Build AND conditions using Toffoli gates
    qc.ccx(q0, q1, a0)  # a0 = q0 AND q1
    qc.ccx(q2, q3, a1)  # a1 = q2 AND q3
    qc.ccx(a0, a1, a2)  # a2 = (q0 AND q1) AND (q2 AND q3)
    
    # PHASE: Apply -1 phase to marked state
    qc.z(a2)
    
    # UNCOMPUTE: Reverse all steps to restore ancillas to |0>
    qc.ccx(a0, a1, a2)
    qc.ccx(q2, q3, a1)
    qc.ccx(q0, q1, a0)
    
    qc.x(q2)
    qc.x(q0)
