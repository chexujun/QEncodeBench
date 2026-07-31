from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    """
    Phase oracle for graph coloring with 5 vertices and 6 edges.
    Applies phase -1 iff all edges connect vertices of different colors.
    """
    edges = [(0, 2), (0, 4), (1, 3), (1, 4), (2, 3), (3, 4)]
    
    # Ancilla usage:
    # ancilla_qubits[0:6] store "edge_bad" flags (1 if edge has same color)
    # ancilla_qubits[6] stores "all_different" flag
    
    # ============ COMPUTE PHASE ============
    
    # For each edge, mark it as "bad" if its endpoints have the same color.
    # Edge (u,v) has same color iff (b0_u + 2*b1_u) % 3 == (b0_v + 2*b1_v) % 3
    # This happens for these (b0_u, b1_u, b0_v, b1_v) cases:
    # (0,0,0,0), (0,0,1,1), (1,0,1,0), (0,1,0,1), (1,1,0,0), (1,1,1,1)
    
    for idx, (u, v) in enumerate(edges):
        b0_u = problem_qubits[2 * u]
        b1_u = problem_qubits[2 * u + 1]
        b0_v = problem_qubits[2 * v]
        b1_v = problem_qubits[2 * v + 1]
        edge_bad = ancilla_qubits[idx]
        
        # Enumerate all color-matching cases
        matching_cases = [
            [0, 0, 0, 0],  # both color 0
            [0, 0, 1, 1],  # both color 0 (via code 3)
            [1, 0, 1, 0],  # both color 1
            [0, 1, 0, 1],  # both color 2
            [1, 1, 0, 0],  # both color 0 (via code 3)
            [1, 1, 1, 1],  # both color 0 (via code 3)
        ]
        
        qubits = [b0_u, b1_u, b0_v, b1_v]
        for case in matching_cases:
            # Flip qubits so this case becomes all 1s
            for i, expected_bit in enumerate(case):
                if expected_bit == 0:
                    qc.x(qubits[i])
            
            # Multi-controlled X: if all controls are 1, flip edge_bad
            qc.mcx(qubits, edge_bad)
            
            # Flip qubits back
            for i, expected_bit in enumerate(case):
                if expected_bit == 0:
                    qc.x(qubits[i])
    
    # Now edge_bad[i] = 1 iff edge i has same-colored endpoints
    
    # Compute all_different = 1 iff no edge is bad
    # Equivalently: all_different = 1 iff all edge_bad[i] = 0
    # Implementation: flip all edge_bad, then use 6-controlled-X on all_different
    
    all_different = ancilla_qubits[6]
    
    for i in range(6):
        qc.x(ancilla_qubits[i])  # Flip: edge_bad[i] -> NOT edge_bad[i]
    
    # Multi-controlled X with 6 controls: all_different = 1 iff all (NOT edge_bad[i]) = 1
    qc.mcx(ancilla_qubits[:6], all_different)
    
    for i in range(6):
        qc.x(ancilla_qubits[i])  # Flip back
    
    # ============ APPLY PHASE ============
    
    # Apply Z gate to all_different: adds phase -1 if it's in state |1>
    # This marks all valid colorings (where all edges have different colors)
    qc.z(all_different)
    
    # ============ UNCOMPUTE PHASE ============
    
    # Uncompute all_different back to |0>
    for i in range(6):
        qc.x(ancilla_qubits[i])
    
    qc.mcx(ancilla_qubits[:6], all_different)
    
    for i in range(6):
        qc.x(ancilla_qubits[i])
    
    # Uncompute edge_bad flags (reverse order, applying same gates)
    for idx in range(5, -1, -1):
        u, v = edges[idx]
        b0_u = problem_qubits[2 * u]
        b1_u = problem_qubits[2 * u + 1]
        b0_v = problem_qubits[2 * v]
        b1_v = problem_qubits[2 * v + 1]
        edge_bad = ancilla_qubits[idx]
        
        matching_cases = [
            [0, 0, 0, 0],
            [0, 0, 1, 1],
            [1, 0, 1, 0],
            [0, 1, 0, 1],
            [1, 1, 0, 0],
            [1, 1, 1, 1],
        ]
        
        qubits = [b0_u, b1_u, b0_v, b1_v]
        for case in matching_cases:
            for i, expected_bit in enumerate(case):
                if expected_bit == 0:
                    qc.x(qubits[i])
            
            qc.mcx(qubits, edge_bad)
            
            for i, expected_bit in enumerate(case):
                if expected_bit == 0:
                    qc.x(qubits[i])
