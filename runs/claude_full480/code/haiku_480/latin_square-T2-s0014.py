def build_oracle(qc, problem_qubits, ancilla_qubits):
    # Extract problem qubits
    # Free cells: (0,0), (1,1), (2,1)
    # Each cell uses 2 qubits: [low bit, high bit]
    b0_0, b1_0 = problem_qubits[0], problem_qubits[1]
    b0_1, b1_1 = problem_qubits[2], problem_qubits[3]
    b0_2, b1_2 = problem_qubits[4], problem_qubits[5]
    
    # Grid is:
    #   . 2 1    Row 0 needs value 0 at (0,0)
    #   1 . 2    Row 1 needs value 0 at (1,1)
    #   2 . 0    Row 2 needs value 1 at (2,1)
    #
    # Code c = b0 + 2*b1 maps to value (c mod 3):
    #   00 → 0,  01 → 1,  10 → 2,  11 → 0
    #
    # Valid completion requires:
    #   Cell 0: value 0 ⟹ b0_0 = b1_0 (codes 00 or 11)
    #   Cell 1: value 0 ⟹ b0_1 = b1_1 (codes 00 or 11)
    #   Cell 2: value 1 ⟹ (b0_2, b1_2) = (1, 0)
    
    # Ancillas
    a_xor0 = ancilla_qubits[0]      # b0_0 XOR b1_0
    a_xor1 = ancilla_qubits[1]      # b0_1 XOR b1_1
    a_b02 = ancilla_qubits[2]       # b0_2
    a_not_b12 = ancilla_qubits[3]   # NOT b1_2
    a_and1 = ancilla_qubits[4]      # AND intermediate
    a_and2 = ancilla_qubits[5]      # AND intermediate
    a_result = ancilla_qubits[6]    # Final AND result
    
    # COMPUTE phase condition
    
    # a_xor0 = b0_0 XOR b1_0
    qc.cx(b0_0, a_xor0)
    qc.cx(b1_0, a_xor0)
    
    # a_xor1 = b0_1 XOR b1_1
    qc.cx(b0_1, a_xor1)
    qc.cx(b1_1, a_xor1)
    
    # a_b02 = b0_2
    qc.cx(b0_2, a_b02)
    
    # a_not_b12 = NOT b1_2
    qc.x(a_not_b12)
    qc.cx(b1_2, a_not_b12)
    
    # Convert XOR results to "equal" signals (negate)
    qc.x(a_xor0)  # a_xor0 ← NOT(b0_0 XOR b1_0)
    qc.x(a_xor1)  # a_xor1 ← NOT(b0_1 XOR b1_1)
    
    # AND all four conditions
    qc.ccx(a_xor0, a_xor1, a_and1)
    qc.ccx(a_and1, a_b02, a_and2)
    qc.ccx(a_and2, a_not_b12, a_result)
    
    # APPLY PHASE
    qc.z(a_result)
    
    # UNCOMPUTE (mirror of compute in reverse)
    qc.ccx(a_and2, a_not_b12, a_result)
    qc.ccx(a_and1, a_b02, a_and2)
    qc.ccx(a_xor0, a_xor1, a_and1)
    
    qc.x(a_xor1)
    qc.x(a_xor0)
    
    qc.cx(b1_2, a_not_b12)
    qc.x(a_not_b12)
    
    qc.cx(b0_2, a_b02)
    
    qc.cx(b0_1, a_xor1)
    qc.cx(b1_1, a_xor1)
    
    qc.cx(b0_0, a_xor0)
    qc.cx(b1_0, a_xor0)
