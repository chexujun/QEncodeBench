from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    """
    Oracle for 5-vertex graph coloring: applies phase -1 to valid colorings
    where all edges connect vertices of different colors.
    
    Each vertex v uses qubits problem_qubits[2v] (low) and problem_qubits[2v+1] (high).
    Color decoding: (low, high) maps to (0,0)->0, (1,0)->1, (0,1)->2, (1,1)->0.
    Valid coloring: edges (0,3), (1,2), (3,4) all have different endpoint colors.
    """
    edges = [(0, 3), (1, 2), (3, 4)]
    
    # Ancilla allocation:
    # 0-2: whether each edge has matching colors (same color = 1)
    # 3: OR of all edge matches (0 iff all edges differ in color)
    edge_match = ancilla_qubits[0:3]
    combined = ancilla_qubits[3]
    
    # Step 1: Compute edge_match[i] for each edge
    for edge_idx, (u, v) in enumerate(edges):
        u_l, u_h = problem_qubits[2*u], problem_qubits[2*u+1]
        v_l, v_h = problem_qubits[2*v], problem_qubits[2*v+1]
        anc = edge_match[edge_idx]
        
        # Match cases: colors are the same for these (u_l, u_h, v_l, v_h) patterns
        # Case 1: (0,0,0,0)
        qc.x([u_l, u_h, v_l, v_h])
        qc.mcx([u_l, u_h, v_l, v_h], anc)
        qc.x([u_l, u_h, v_l, v_h])
        
        # Case 2: (0,0,1,1)
        qc.x([u_l, u_h])
        qc.mcx([u_l, u_h, v_l, v_h], anc)
        qc.x([u_l, u_h])
        
        # Case 3: (1,0,1,0)
        qc.x([u_h, v_h])
        qc.mcx([u_l, u_h, v_l, v_h], anc)
        qc.x([u_h, v_h])
        
        # Case 4: (0,1,0,1)
        qc.x([u_l, v_l])
        qc.mcx([u_l, u_h, v_l, v_h], anc)
        qc.x([u_l, v_l])
        
        # Case 5: (1,1,0,0)
        qc.x([v_l, v_h])
        qc.mcx([u_l, u_h, v_l, v_h], anc)
        qc.x([v_l, v_h])
        
        # Case 6: (1,1,1,1)
        qc.mcx([u_l, u_h, v_l, v_h], anc)
    
    # Step 2: OR all edge_match flags into combined
    for i in range(3):
        qc.cx(edge_match[i], combined)
    
    # Step 3: Apply Z gate if combined == 0 (meaning all edges differ)
    qc.x(combined)      # flip: combined=0 becomes 1
    qc.z(combined)      # apply phase to qubit set to 1
    qc.x(combined)      # flip back
    
    # Step 4: Uncompute OR
    for i in range(3):
        qc.cx(edge_match[i], combined)
    
    # Step 5: Uncompute edge matching (in reverse order)
    for edge_idx in range(len(edges) - 1, -1, -1):
        u, v = edges[edge_idx]
        u_l, u_h = problem_qubits[2*u], problem_qubits[2*u+1]
        v_l, v_h = problem_qubits[2*v], problem_qubits[2*v+1]
        anc = edge_match[edge_idx]
        
        qc.mcx([u_l, u_h, v_l, v_h], anc)
        
        qc.x([v_l, v_h])
        qc.mcx([u_l, u_h, v_l, v_h], anc)
        qc.x([v_l, v_h])
        
        qc.x([u_l, v_l])
        qc.mcx([u_l, u_h, v_l, v_h], anc)
        qc.x([u_l, v_l])
        
        qc.x([u_h, v_h])
        qc.mcx([u_l, u_h, v_l, v_h], anc)
        qc.x([u_h, v_h])
        
        qc.x([u_l, u_h])
        qc.mcx([u_l, u_h, v_l, v_h], anc)
        qc.x([u_l, u_h])
        
        qc.x([u_l, u_h, v_l, v_h])
        qc.mcx([u_l, u_h, v_l, v_h], anc)
        qc.x([u_l, u_h, v_l, v_h])
