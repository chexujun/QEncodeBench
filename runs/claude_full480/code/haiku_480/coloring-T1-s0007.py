def build_oracle(qc, problem_qubits, ancilla_qubits):
    b0_0, b1_0, b0_1, b1_1, b0_2, b1_2 = problem_qubits
    anc0, anc1, anc2, anc3 = ancilla_qubits
    
    def apply_controlled_term(qubits_list, control_states, target):
        """Apply multi-controlled X with specified control states."""
        # Apply X gates for qubits that should be in state 0
        for i, state in enumerate(control_states):
            if state == 0:
                qc.x(qubits_list[i])
        # Apply multi-controlled X
        qc.mcx(qubits_list, target)
        # Undo X gates
        for i, state in enumerate(control_states):
            if state == 0:
                qc.x(qubits_list[i])
    
    # For each edge, compute when colors are the SAME (bad condition)
    # Two 2-bit codes (c_u, c_v) represent the same color when:
    # (code_u=00 and code_v=00) or (code_u=00 and code_v=11) or
    # (code_u=11 and code_v=00) or (code_u=11 and code_v=11) or
    # (code_u=01 and code_v=01) or (code_u=10 and code_v=10)
    
    # Compute bad_01 into anc0
    edge01 = [b0_0, b1_0, b0_1, b1_1]
    apply_controlled_term(edge01, [0, 0, 0, 0], anc0)
    apply_controlled_term(edge01, [0, 0, 1, 1], anc0)
    apply_controlled_term(edge01, [1, 1, 0, 0], anc0)
    apply_controlled_term(edge01, [1, 1, 1, 1], anc0)
    apply_controlled_term(edge01, [1, 0, 1, 0], anc0)
    apply_controlled_term(edge01, [0, 1, 0, 1], anc0)
    
    # Compute bad_02 into anc1
    edge02 = [b0_0, b1_0, b0_2, b1_2]
    apply_controlled_term(edge02, [0, 0, 0, 0], anc1)
    apply_controlled_term(edge02, [0, 0, 1, 1], anc1)
    apply_controlled_term(edge02, [1, 1, 0, 0], anc1)
    apply_controlled_term(edge02, [1, 1, 1, 1], anc1)
    apply_controlled_term(edge02, [1, 0, 1, 0], anc1)
    apply_controlled_term(edge02, [0, 1, 0, 1], anc1)
    
    # Compute bad_12 into anc2
    edge12 = [b0_1, b1_1, b0_2, b1_2]
    apply_controlled_term(edge12, [0, 0, 0, 0], anc2)
    apply_controlled_term(edge12, [0, 0, 1, 1], anc2)
    apply_controlled_term(edge12, [1, 1, 0, 0], anc2)
    apply_controlled_term(edge12, [1, 1, 1, 1], anc2)
    apply_controlled_term(edge12, [1, 0, 1, 0], anc2)
    apply_controlled_term(edge12, [0, 1, 0, 1], anc2)
    
    # Invert: convert bad -> good
    qc.x(anc0)
    qc.x(anc1)
    qc.x(anc2)
    
    # Compute: all_good = good_01 AND good_02 AND good_12 into anc3
    qc.mcx([anc0, anc1, anc2], anc3)
    
    # Apply phase -1 when all constraints are satisfied
    qc.z(anc3)
    
    # Uncompute: all_good
    qc.mcx([anc0, anc1, anc2], anc3)
    
    # Undo inversion
    qc.x(anc0)
    qc.x(anc1)
    qc.x(anc2)
    
    # Uncompute bad edges in reverse order
    apply_controlled_term(edge12, [0, 1, 0, 1], anc2)
    apply_controlled_term(edge12, [1, 0, 1, 0], anc2)
    apply_controlled_term(edge12, [1, 1, 1, 1], anc2)
    apply_controlled_term(edge12, [1, 1, 0, 0], anc2)
    apply_controlled_term(edge12, [0, 0, 1, 1], anc2)
    apply_controlled_term(edge12, [0, 0, 0, 0], anc2)
    
    apply_controlled_term(edge02, [0, 1, 0, 1], anc1)
    apply_controlled_term(edge02, [1, 0, 1, 0], anc1)
    apply_controlled_term(edge02, [1, 1, 1, 1], anc1)
    apply_controlled_term(edge02, [1, 1, 0, 0], anc1)
    apply_controlled_term(edge02, [0, 0, 1, 1], anc1)
    apply_controlled_term(edge02, [0, 0, 0, 0], anc1)
    
    apply_controlled_term(edge01, [0, 1, 0, 1], anc0)
    apply_controlled_term(edge01, [1, 0, 1, 0], anc0)
    apply_controlled_term(edge01, [1, 1, 1, 1], anc0)
    apply_controlled_term(edge01, [1, 1, 0, 0], anc0)
    apply_controlled_term(edge01, [0, 0, 1, 1], anc0)
    apply_controlled_term(edge01, [0, 0, 0, 0], anc0)
