def build_oracle(qc, problem_qubits, ancilla_qubits):
    edges = [(0, 2), (0, 5), (1, 2), (1, 4), (1, 5), (2, 4), (3, 4), (4, 5)]
    
    # Ancilla allocation (11 total)
    edges_covered = ancilla_qubits[0:8]  # 8 qubits: one per edge
    all_covered = ancilla_qubits[8]      # 1 qubit: AND of all edges
    weight_le_4 = ancilla_qubits[9]      # 1 qubit: 1 iff hamming weight <= 4
    solution = ancilla_qubits[10]        # 1 qubit: final solution bit
    
    # === COMPUTE PHASE ===
    
    # Compute edges_covered[i] = problem_qubits[u_i] OR problem_qubits[v_i] for each edge
    # Using: OR(a,b) into target = cx(a,target); cx(b,target); ccx(a,b,target)
    for i, (u, v) in enumerate(edges):
        qc.cx(problem_qubits[u], edges_covered[i])
        qc.cx(problem_qubits[v], edges_covered[i])
        qc.ccx(problem_qubits[u], problem_qubits[v], edges_covered[i])
    
    # Compute all_covered = AND of all edge_covered flags
    qc.mcx(edges_covered, all_covered)
    
    # Compute weight_le_4: 1 iff hamming weight <= 4
    # Initialize to 1, then flip to 0 if weight > 4 (i.e., weight >= 5)
    qc.x(weight_le_4)
    
    # Check if all 6 problem qubits are 1 (weight = 6)
    qc.mcx(problem_qubits, edges_covered[0])
    qc.cx(edges_covered[0], weight_le_4)
    
    # Check if exactly 5 problem qubits are 1 (weight = 5)
    # For each qubit i, check if only qubit i is 0 and rest are 1
    for i in range(6):
        qc.x(problem_qubits[i])           # Flip qubit i
        qc.mcx(problem_qubits, edges_covered[1])  # Check if all are now 1
        qc.x(problem_qubits[i])           # Flip qubit i back
        qc.cx(edges_covered[1], weight_le_4)  # Flip weight_le_4 if exactly 5 ones
    
    # Compute solution = all_covered AND weight_le_4
    qc.ccx(all_covered, weight_le_4, solution)
    
    # === APPLY PHASE ===
    qc.z(solution)
    
    # === UNCOMPUTE ===
    
    # Uncompute solution
    qc.ccx(all_covered, weight_le_4, solution)
    
    # Uncompute weight_le_4 (reverse order)
    for i in range(5, -1, -1):
        qc.cx(edges_covered[1], weight_le_4)
        qc.x(problem_qubits[i])
        qc.mcx(problem_qubits, edges_covered[1])
        qc.x(problem_qubits[i])
    
    qc.cx(edges_covered[0], weight_le_4)
    qc.mcx(problem_qubits, edges_covered[0])
    qc.x(weight_le_4)
    
    # Uncompute all_covered
    qc.mcx(edges_covered, all_covered)
    
    # Uncompute edges_covered (reverse order)
    for i in range(7, -1, -1):
        u, v = edges[i]
        qc.ccx(problem_qubits[u], problem_qubits[v], edges_covered[i])
        qc.cx(problem_qubits[v], edges_covered[i])
        qc.cx(problem_qubits[u], edges_covered[i])
