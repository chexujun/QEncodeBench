from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    """
    Oracle for graph coloring on 4 vertices with edges (0,1), (0,2), (1,2), (1,3).
    Each vertex uses 2 qubits encoding a color: c = b0 + 2*b1.
    Decoding: 0,3 -> color 0; 1 -> color 1; 2 -> color 2.
    Oracle marks states where all edges connect vertices of different colors.
    """
    edges = [(0, 1), (0, 2), (1, 2), (1, 3)]
    
    # Allocate ancillas: [0:4] for edge constraint flags, [4] for final AND result
    edge_flags = ancilla_qubits[0:4]
    final_flag = ancilla_qubits[4]
    
    # Compute: edge_flags[i] = 1 iff colors at edge[i] are different
    for i, (u, v) in enumerate(edges):
        compute_edge_constraint(qc, problem_qubits, u, v, edge_flags[i])
    
    # Compute: final_flag = edge_flags[0] AND edge_flags[1] AND edge_flags[2] AND edge_flags[3]
    qc.mcx(edge_flags, final_flag)
    
    # Apply phase: -1 iff final_flag = 1 (all edges have different colors)
    qc.z(final_flag)
    
    # Uncompute: reverse the AND operation
    qc.mcx(edge_flags, final_flag)
    
    # Uncompute edge constraints in reverse order
    for i in range(len(edges) - 1, -1, -1):
        u, v = edges[i]
        compute_edge_constraint(qc, problem_qubits, u, v, edge_flags[i])


def compute_edge_constraint(qc, problem_qubits, u, v, result_ancilla):
    """
    Compute whether vertices u and v have different colors.
    Set result_ancilla = 1 if colors differ, 0 if same.
    
    Two 2-bit codes have same color iff:
    - Both decode to 0: (b0 XNOR b1) holds for both
    - Both decode to 1: (b0=1, b1=0) for both
    - Both decode to 2: (b0=0, b1=1) for both
    """
    u0 = problem_qubits[2*u]
    u1 = problem_qubits[2*u + 1]
    v0 = problem_qubits[2*v]
    v1 = problem_qubits[2*v + 1]
    
    # The 6 2-qubit patterns where colors are identical:
    same_color_patterns = [
        [0, 0, 0, 0],  # decode 0, 0
        [0, 0, 1, 1],  # decode 0, 0
        [1, 1, 0, 0],  # decode 0, 0
        [1, 1, 1, 1],  # decode 0, 0
        [1, 0, 1, 0],  # decode 1, 1
        [0, 1, 0, 1],  # decode 2, 2
    ]
    
    qubits = [u0, u1, v0, v1]
    
    # For each pattern, flip result_ancilla if pattern matches
    # (Using multi-controlled X: flips target iff all controls = 1)
    for pattern in same_color_patterns:
        # Flip qubits that must be 0 for pattern matching
        for qubit, expected in zip(qubits, pattern):
            if expected == 0:
                qc.x(qubit)
        
        # Multi-controlled X: flips result_ancilla iff all qubits = 1
        qc.mcx(qubits, result_ancilla)
        
        # Restore qubits
        for qubit, expected in zip(qubits, pattern):
            if expected == 0:
                qc.x(qubit)
    
    # At this point, result_ancilla = 1 iff colors are same
    # Flip to get: result_ancilla = 1 iff colors are different
    qc.x(result_ancilla)
