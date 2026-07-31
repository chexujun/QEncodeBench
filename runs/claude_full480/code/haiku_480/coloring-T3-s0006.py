from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0,1), (0,3), (0,4), (1,2), (1,3), (1,4), (2,3), (2,4)]
    
    def compute_edge_differs(u, v, result_anc, temp_anc_list):
        """Compute if colors differ for edge (u,v) into result_anc.
        Assumes result_anc and temp_anc_list are in |0> state.
        Leaves all ancillas in |0> state after computation.
        """
        u_b0 = problem_qubits[2*u]
        u_b1 = problem_qubits[2*u + 1]
        v_b0 = problem_qubits[2*v]
        v_b1 = problem_qubits[2*v + 1]
        
        t1, t2, t3 = temp_anc_list[0], temp_anc_list[1], temp_anc_list[2]
        
        # Compute: u_same_bits = NOT(u_b0 XOR u_b1) into t1
        qc.cx(u_b0, t1)
        qc.cx(u_b1, t1)
        qc.x(t1)
        
        # Compute: v_same_bits = NOT(v_b0 XOR v_b1) into t2
        qc.cx(v_b0, t2)
        qc.cx(v_b1, t2)
        qc.x(t2)
        
        # Compute: colors_same = u_same_bits AND v_same_bits into t3
        qc.ccx(t1, t2, t3)
        
        # Compute: result = NOT(colors_same) into result_anc
        qc.x(t3)
        qc.cx(t3, result_anc)
        
        # Uncompute: restore t1, t2, t3 to |0>
        qc.x(result_anc)
        qc.cx(t3, result_anc)
        qc.x(t3)
        qc.ccx(t1, t2, t3)
        qc.x(t2)
        qc.cx(v_b1, t2)
        qc.cx(v_b0, t2)
        qc.x(t1)
        qc.cx(u_b1, t1)
        qc.cx(u_b0, t1)
    
    # Process edges in groups, accumulating ANDs
    # Use anc[4] for first group of 4 edges
    # Use anc[3] for second group of 4 edges
    # Use anc[0] for final AND, where phase is applied
    
    result1 = ancilla_qubits[4]  # Accumulator for edges 0-3
    result2 = ancilla_qubits[3]  # Accumulator for edges 4-7
    final_result = ancilla_qubits[0]  # Final result where phase is applied
    
    qc.x(result1)  # Initialize to |1>
    
    for i in range(4):
        u, v = edges[i]
        compute_edge_differs(u, v, ancilla_qubits[1], 
                            [ancilla_qubits[2], ancilla_qubits[3], ancilla_qubits[4]])
        # Now anc[1] = colors_differ for edge i
        # AND into result1
        qc.ccx(result1, ancilla_qubits[1], ancilla_qubits[2])
        qc.cx(ancilla_qubits[2], result1)
        qc.ccx(result1, ancilla_qubits[1], ancilla_qubits[2])
        # Uncompute anc[1]
        qc.x(ancilla_qubits[1])
    
    qc.x(result2)  # Initialize to |1>
    
    for i in range(4, 8):
        u, v = edges[i]
        compute_edge_differs(u, v, ancilla_qubits[1], 
                            [ancilla_qubits[2], ancilla_qubits[3], ancilla_qubits[4]])
        # AND into result2
        qc.ccx(result2, ancilla_qubits[1], ancilla_qubits[2])
        qc.cx(ancilla_qubits[2], result2)
        qc.ccx(result2, ancilla_qubits[1], ancilla_qubits[2])
        qc.x(ancilla_qubits[1])
    
    # Final AND: final_result = result1 AND result2
    qc.x(final_result)
    qc.ccx(final_result, result1, ancilla_qubits[1])
    qc.ccx(ancilla_qubits[1], result2, ancilla_qubits[2])
    qc.cx(ancilla_qubits[2], final_result)
    qc.ccx(ancilla_qubits[1], result2, ancilla_qubits[2])
    qc.ccx(final_result, result1, ancilla_qubits[1])
    
    # Apply phase gate on final_result
    qc.z(final_result)
    
    # Uncompute the accumulation
    qc.ccx(final_result, result1, ancilla_qubits[1])
    qc.ccx(ancilla_qubits[1], result2, ancilla_qubits[2])
    qc.cx(ancilla_qubits[2], final_result)
    qc.ccx(ancilla_qubits[1], result2, ancilla_qubits[2])
    qc.ccx(final_result, result1, ancilla_qubits[1])
    qc.x(final_result)
