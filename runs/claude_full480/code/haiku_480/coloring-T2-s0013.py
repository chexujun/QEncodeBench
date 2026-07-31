def build_oracle(qc, problem_qubits, ancilla_qubits):
    edges = [(0, 4), (1, 2), (1, 4), (2, 3), (2, 4)]
    
    edge_ancillas = ancilla_qubits[:5]
    target_ancilla = ancilla_qubits[5]
    
    # Compute each edge condition
    for i, (u, v) in enumerate(edges):
        u_idx = 2 * u
        v_idx = 2 * v
        b0_u = problem_qubits[u_idx]
        b1_u = problem_qubits[u_idx + 1]
        b0_v = problem_qubits[v_idx]
        b1_v = problem_qubits[v_idx + 1]
        
        # Compute diff_color into edge_ancillas[i]
        # diff_color = (b0_u XOR b0_v) XOR (b1_u XOR b1_v)
        qc.cx(b0_u, edge_ancillas[i])
        qc.cx(b0_v, edge_ancillas[i])
        qc.cx(b1_u, edge_ancillas[i])
        qc.cx(b1_v, edge_ancillas[i])
    
    # Apply multi-controlled X
    qc.mcx(edge_ancillas, target_ancilla)
    
    # Apply Z phase
    qc.z(target_ancilla)
    
    # Uncompute multi-controlled X
    qc.mcx(edge_ancillas, target_ancilla)
    
    # Uncompute edge conditions
    for i, (u, v) in enumerate(edges):
        u_idx = 2 * u
        v_idx = 2 * v
        b0_u = problem_qubits[u_idx]
        b1_u = problem_qubits[u_idx + 1]
        b0_v = problem_qubits[v_idx]
        b1_v = problem_qubits[v_idx + 1]
        
        # Uncompute diff_color
        qc.cx(b1_v, edge_ancillas[i])
        qc.cx(b1_u, edge_ancillas[i])
        qc.cx(b0_v, edge_ancillas[i])
        qc.cx(b0_u, edge_ancillas[i])
