from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Extract vertex bit pairs: vertex v has bits at problem_qubits[2v:2v+2]
    v = [[problem_qubits[2*i], problem_qubits[2*i+1]] for i in range(4)]
    
    # Edges to check: (0,3), (1,2), (1,3), (2,3)
    edges = [(0, 3), (1, 2), (1, 3), (2, 3)]
    
    a = ancilla_qubits
    
    # Patterns where an edge has SAME color on both endpoints (violations):
    # Color mapping: (b0,b1) -> (b0 + 2*b1) mod 3
    # (00)->0, (01)->2, (10)->1, (11)->0
    # Same color occurs for: (00,00), (00,11), (01,01), (10,10), (11,00), (11,11)
    violation_patterns = [
        [0, 0, 0, 0],  # Both (00) -> color 0
        [0, 0, 1, 1],  # (00) and (11) -> both color 0
        [1, 0, 1, 0],  # Both (10) -> color 1
        [0, 1, 0, 1],  # Both (01) -> color 2
        [1, 1, 0, 0],  # (11) and (00) -> both color 0
        [1, 1, 1, 1],  # Both (11) -> color 0
    ]
    
    # Step 1: Compute violation flag for each edge
    for edge_idx, (vi, vj) in enumerate(edges):
        b0_i, b1_i = v[vi]
        b0_j, b1_j = v[vj]
        violation = a[edge_idx]
        
        qubits = [b0_i, b1_i, b0_j, b1_j]
        
        for pattern_bits in violation_patterns:
            # Check if current state matches this violation pattern
            controls = []
            for q, expected in zip(qubits, pattern_bits):
                if expected == 1:
                    controls.append(q)
                else:
                    qc.x(q)
                    controls.append(q)
            
            # Flip violation qubit if pattern matches
            qc.mcx(controls, violation)
            
            # Undo X gates
            for q, expected in zip(qubits, pattern_bits):
                if expected == 0:
                    qc.x(q)
    
    # Step 2: Compute result = 1 iff all violations are 0
    result = a[4]
    
    # Negate all violation qubits
    for i in range(4):
        qc.x(a[i])
    
    # Multi-controlled X: result = 1 iff all (negated) violations are 1
    # i.e., iff all original violations are 0
    qc.mcx([a[0], a[1], a[2], a[3]], result)
    
    # Undo negation
    for i in range(4):
        qc.x(a[i])
    
    # Step 3: Apply phase -1
    qc.z(result)
    
    # Step 4: Uncompute (reverse order)
    for i in range(4):
        qc.x(a[i])
    
    qc.mcx([a[0], a[1], a[2], a[3]], result)
    
    for i in range(4):
        qc.x(a[i])
    
    # Uncompute violations (reverse order)
    for edge_idx, (vi, vj) in enumerate(edges):
        b0_i, b1_i = v[vi]
        b0_j, b1_j = v[vj]
        violation = a[edge_idx]
        
        qubits = [b0_i, b1_i, b0_j, b1_j]
        
        for pattern_bits in reversed(violation_patterns):
            controls = []
            for q, expected in zip(qubits, pattern_bits):
                if expected == 1:
                    controls.append(q)
                else:
                    qc.x(q)
                    controls.append(q)
            
            qc.mcx(controls, violation)
            
            for q, expected in zip(qubits, pattern_bits):
                if expected == 0:
                    qc.x(q)
