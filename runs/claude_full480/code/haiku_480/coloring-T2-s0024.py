def build_oracle(qc, problem_qubits, ancilla_qubits):
    edges = [(0,1), (0,2), (0,3), (0,4), (1,4), (2,3), (2,4)]
    
    # Truth table: for each 4-bit input (q0_u, q1_u, q0_v, q1_v),
    # colors_differ is true at these indices
    indices_colors_differ = [1, 2, 4, 6, 7, 8, 9, 11, 13, 14]
    
    # Compute the edge constraints into ancillas 0..6
    for i, (u, v) in enumerate(edges):
        q0_u = problem_qubits[2*u]
        q1_u = problem_qubits[2*u + 1]
        q0_v = problem_qubits[2*v]
        q1_v = problem_qubits[2*v + 1]
        edge_anc = ancilla_qubits[i]
        
        # Compute: colors differ at vertex u vs vertex v
        # Encoding: code = q0 + 2*q1, color = code % 3 (with 3->0)
        # colors_differ = colors[u] != colors[v]
        for idx in indices_colors_differ:
            b0 = (idx >> 0) & 1
            b1 = (idx >> 1) & 1
            b2 = (idx >> 2) & 1
            b3 = (idx >> 3) & 1
            
            if b0 == 0:
                qc.x(q0_u)
            if b1 == 0:
                qc.x(q1_u)
            if b2 == 0:
                qc.x(q0_v)
            if b3 == 0:
                qc.x(q1_v)
            
            qc.mcx([q0_u, q1_u, q0_v, q1_v], edge_anc)
            
            if b0 == 0:
                qc.x(q0_u)
            if b1 == 0:
                qc.x(q1_u)
            if b2 == 0:
                qc.x(q0_v)
            if b3 == 0:
                qc.x(q1_v)
    
    # AND all 7 edge constraints into ancilla 7 (phase qubit)
    result_anc = ancilla_qubits[7]
    qc.mcx(ancilla_qubits[:7], result_anc)
    
    # Apply phase: Z gate flips sign when ancilla is |1>
    qc.z(result_anc)
    
    # Uncompute: reverse the AND operation and all edge constraints
    qc.mcx(ancilla_qubits[:7], result_anc)
    
    for i in range(6, -1, -1):
        (u, v) = edges[i]
        q0_u = problem_qubits[2*u]
        q1_u = problem_qubits[2*u + 1]
        q0_v = problem_qubits[2*v]
        q1_v = problem_qubits[2*v + 1]
        edge_anc = ancilla_qubits[i]
        
        for idx in reversed(indices_colors_differ):
            b0 = (idx >> 0) & 1
            b1 = (idx >> 1) & 1
            b2 = (idx >> 2) & 1
            b3 = (idx >> 3) & 1
            
            if b0 == 0:
                qc.x(q0_u)
            if b1 == 0:
                qc.x(q1_u)
            if b2 == 0:
                qc.x(q0_v)
            if b3 == 0:
                qc.x(q1_v)
            
            qc.mcx([q0_u, q1_u, q0_v, q1_v], edge_anc)
            
            if b0 == 0:
                qc.x(q0_u)
            if b1 == 0:
                qc.x(q1_u)
            if b2 == 0:
                qc.x(q0_v)
            if b3 == 0:
                qc.x(q1_v)
