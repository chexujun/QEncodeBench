from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    """
    Grover oracle for graph 3-coloring.
    
    Vertex v's color is encoded by 2 qubits at indices 2v (low) and 2v+1 (high):
    - Code 00 -> color 0
    - Code 01 -> color 1
    - Code 10 -> color 2
    - Code 11 -> color 0 (surjective)
    
    Two vertices have the SAME color (monochromatic edge) iff:
    - Both have a_u XOR b_u = 0 and a_v XOR b_v = 0 (both color 0), OR
    - (a_u=1, b_u=0) AND (a_v=1, b_v=0) (both color 1), OR
    - (a_u=0, b_u=1) AND (a_v=0, b_v=1) (both color 2)
    
    This corresponds to binary patterns: 0000, 0011, 0101, 1010, 1100, 1111.
    """
    
    # Extract color bit indices for each vertex
    vertices = [(problem_qubits[2*v], problem_qubits[2*v+1]) for v in range(5)]
    
    # Edges that must have different colors
    edges = [(0,2), (0,4), (1,2), (1,4), (2,3), (2,4)]
    
    # Allocate ancillas: 6 for edge predicates, 1 for final result
    edge_valid = ancilla_qubits[:6]
    result = ancilla_qubits[6]
    
    # Monochromatic (invalid) color patterns for (a_u, b_u, a_v, b_v)
    monochromatic_patterns = [
        (0, 0, 0, 0),  # color 0 vs color 0
        (0, 0, 1, 1),  # color 0 vs color 0
        (1, 0, 1, 0),  # color 1 vs color 1
        (0, 1, 0, 1),  # color 2 vs color 2
        (1, 1, 0, 0),  # color 0 vs color 0
        (1, 1, 1, 1),  # color 0 vs color 0
    ]
    
    # Step 1: Compute edge predicates
    for edge_idx, (u, v) in enumerate(edges):
        a_u, b_u = vertices[u]
        a_v, b_v = vertices[v]
        
        # Mark monochromatic (invalid) cases using controlled-X with flipped controls
        for (cu, cbu, cv, cbv) in monochromatic_patterns:
            # Apply X to flip qubits where pattern expects 0
            if cu == 0:
                qc.x(a_u)
            if cbu == 0:
                qc.x(b_u)
            if cv == 0:
                qc.x(a_v)
            if cbv == 0:
                qc.x(b_v)
            
            # Apply multi-controlled X (increments edge_valid if pattern matches)
            qc.mcx([a_u, b_u, a_v, b_v], edge_valid[edge_idx])
            
            # Unflip controls
            if cbv == 0:
                qc.x(b_v)
            if cv == 0:
                qc.x(a_v)
            if cbu == 0:
                qc.x(b_u)
            if cu == 0:
                qc.x(a_u)
        
        # Invert: mark valid edges (different colors)
        qc.x(edge_valid[edge_idx])
    
    # Step 2: Compute AND of all edge predicates into result
    qc.mcx(edge_valid, result)
    
    # Step 3: Apply phase flip
    qc.z(result)
    
    # Step 4: Uncompute AND (result back to |0>)
    qc.mcx(edge_valid, result)
    
    # Step 5: Uncompute edge predicates (reverse computation)
    for edge_idx, (u, v) in enumerate(edges):
        a_u, b_u = vertices[u]
        a_v, b_v = vertices[v]
        
        # Invert back to mark monochromatic cases again
        qc.x(edge_valid[edge_idx])
        
        # Reverse: unmark monochromatic cases in reverse order
        for (cu, cbu, cv, cbv) in reversed(monochromatic_patterns):
            if cu == 0:
                qc.x(a_u)
            if cbu == 0:
                qc.x(b_u)
            if cv == 0:
                qc.x(a_v)
            if cbv == 0:
                qc.x(b_v)
            
            qc.mcx([a_u, b_u, a_v, b_v], edge_valid[edge_idx])
            
            if cbv == 0:
                qc.x(b_v)
            if cv == 0:
                qc.x(a_v)
            if cbu == 0:
                qc.x(b_u)
            if cu == 0:
                qc.x(a_u)
