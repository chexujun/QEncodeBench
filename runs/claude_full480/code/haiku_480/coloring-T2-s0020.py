def build_oracle(qc, problem_qubits, ancilla_qubits):
    edges = [(0,1), (0,2), (0,3), (0,4), (1,4), (2,3), (3,4)]
    
    result_qubit = ancilla_qubits[0]
    temp_edge_qubits = ancilla_qubits[1:8]
    
    def compute_same_color(qc, u0, u1, v0, v1, edge_violated):
        """
        Compute whether two 2-bit color codes decode to the same color.
        Codes: (0,0)->0, (1,0)->1, (0,1)->2, (1,1)->0.
        Same color occurs in 6 cases; toggle edge_violated for each.
        """
        # Case 1: (0,0) and (0,0) -> color 0
        qc.x(u0); qc.x(u1); qc.x(v0); qc.x(v1)
        qc.mcx([u0, u1, v0, v1], edge_violated)
        qc.x(u0); qc.x(u1); qc.x(v0); qc.x(v1)
        
        # Case 2: (1,0) and (1,0) -> color 1
        qc.x(u1); qc.x(v1)
        qc.mcx([u0, u1, v0, v1], edge_violated)
        qc.x(u1); qc.x(v1)
        
        # Case 3: (0,1) and (0,1) -> color 2
        qc.x(u0); qc.x(v0)
        qc.mcx([u0, u1, v0, v1], edge_violated)
        qc.x(u0); qc.x(v0)
        
        # Case 4: (1,1) and (1,1) -> color 0
        qc.mcx([u0, u1, v0, v1], edge_violated)
        
        # Case 5: (0,0) and (1,1) -> both color 0
        qc.x(u0); qc.x(u1)
        qc.mcx([u0, u1, v0, v1], edge_violated)
        qc.x(u0); qc.x(u1)
        
        # Case 6: (1,1) and (0,0) -> both color 0
        qc.x(v0); qc.x(v1)
        qc.mcx([u0, u1, v0, v1], edge_violated)
        qc.x(v0); qc.x(v1)
    
    # COMPUTE PHASE: compute whether each edge has same-colored endpoints
    for (u, v), temp_qubit in zip(edges, temp_edge_qubits):
        u0, u1 = problem_qubits[2*u], problem_qubits[2*u+1]
        v0, v1 = problem_qubits[2*v], problem_qubits[2*v+1]
        compute_same_color(qc, u0, u1, v0, v1, temp_qubit)
    
    # Initialize result qubit to |1⟩
    qc.x(result_qubit)
    
    # Compute result = AND(NOT temp[i]) by chaining CCX gates
    # If any edge has same-colored endpoints, result becomes |0⟩
    for temp_qubit in temp_edge_qubits:
        qc.ccx(temp_qubit, result_qubit, result_qubit)
    
    # APPLY PHASE: Z gate applies -1 phase to |1⟩ state (valid colorings)
    qc.z(result_qubit)
    
    # UNCOMPUTE PHASE: mirror of compute phase
    # Undo the AND computation
    for temp_qubit in reversed(temp_edge_qubits):
        qc.ccx(temp_qubit, result_qubit, result_qubit)
    qc.x(result_qubit)
    
    # Undo the same-color computations for each edge
    for (u, v), temp_qubit in zip(reversed(edges), reversed(temp_edge_qubits)):
        u0, u1 = problem_qubits[2*u], problem_qubits[2*u+1]
        v0, v1 = problem_qubits[2*v], problem_qubits[2*v+1]
        compute_same_color(qc, u0, u1, v0, v1, temp_qubit)
