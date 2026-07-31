from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    """
    Grover oracle for graph 3-coloring constraint verification.
    Applies phase -1 to states where all edges have different colors.
    """
    edges = [(0,1), (0,3), (0,4), (1,2), (1,3), (2,3), (2,4), (3,4)]
    
    # Reserve ancillas: 8 for per-edge flags, 1 for AND result
    same_color = [ancilla_qubits[i] for i in range(8)]
    and_result = ancilla_qubits[8]
    
    # === COMPUTE PHASE ===
    # For each edge, compute whether endpoints have the same color.
    # Colors are computed as: color = (b0 + 2*b1) mod 3
    
    for edge_idx, (u, v) in enumerate(edges):
        u_b0 = problem_qubits[2*u]
        u_b1 = problem_qubits[2*u + 1]
        v_b0 = problem_qubits[2*v]
        v_b1 = problem_qubits[2*v + 1]
        
        sc = same_color[edge_idx]
        
        # Compute same_color using the XOR-based predicate
        qc.cx(u_b0, sc)
        qc.cx(v_b0, sc)
        qc.cx(u_b1, sc)
        qc.cx(v_b1, sc)
        qc.x(sc)
    
    # Compute AND(same_color[0..7]) -> and_result
    qc.mcx(same_color, and_result)
    
    # Flip to get validity flag (1 iff coloring valid)
    qc.x(and_result)
    
    # Apply Z gate for phase -1 on valid colorings
    qc.z(and_result)
    
    # === UNCOMPUTE PHASE ===
    qc.x(and_result)
    qc.mcx(same_color, and_result)
    
    # Reverse same_color computations
    for edge_idx, (u, v) in enumerate(edges):
        u_b0 = problem_qubits[2*u]
        u_b1 = problem_qubits[2*u + 1]
        v_b0 = problem_qubits[2*v]
        v_b1 = problem_qubits[2*v + 1]
        
        sc = same_color[edge_idx]
        
        qc.x(sc)
        qc.cx(v_b1, sc)
        qc.cx(u_b1, sc)
        qc.cx(v_b0, sc)
        qc.cx(u_b0, sc)
