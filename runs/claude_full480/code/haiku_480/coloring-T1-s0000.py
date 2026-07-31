from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Edges: (0,2), (1,2), (1,3), (2,3)
    edges = [(0, 2), (1, 2), (1, 3), (2, 3)]
    
    # Ancilla assignment
    edge_ancillas = [ancilla_qubits[i] for i in range(4)]
    valid_ancilla = ancilla_qubits[4]
    
    def get_vertex_qubits(v):
        return problem_qubits[2*v], problem_qubits[2*v+1]
    
    def compute_same_color_into_anc(b0_u, b1_u, b0_v, b1_v, anc):
        # same_color is true for these code pairs (decoded color is same):
        # (0,0): all bits 0
        # (0,3): b0_u,b1_u = 0,0 and b0_v,b1_v = 1,1
        # (1,1): b0_u,b1_u = 1,0 and b0_v,b1_v = 1,0
        # (2,2): b0_u,b1_u = 0,1 and b0_v,b1_v = 0,1
        # (3,0): b0_u,b1_u = 1,1 and b0_v,b1_v = 0,0
        # (3,3): all bits 1
        
        # Case (0,0): NOT b0_u AND NOT b1_u AND NOT b0_v AND NOT b1_v
        qc.x([b0_u, b1_u, b0_v, b1_v])
        qc.mcx([b0_u, b1_u, b0_v, b1_v], anc)
        qc.x([b0_u, b1_u, b0_v, b1_v])
        
        # Case (0,3): NOT b0_u AND NOT b1_u AND b0_v AND b1_v
        qc.x([b0_u, b1_u])
        qc.mcx([b0_u, b1_u, b0_v, b1_v], anc)
        qc.x([b0_u, b1_u])
        
        # Case (1,1): b0_u AND NOT b1_u AND b0_v AND NOT b1_v
        qc.x([b1_u, b1_v])
        qc.mcx([b0_u, b1_u, b0_v, b1_v], anc)
        qc.x([b1_u, b1_v])
        
        # Case (2,2): NOT b0_u AND b1_u AND NOT b0_v AND b1_v
        qc.x([b0_u, b0_v])
        qc.mcx([b0_u, b1_u, b0_v, b1_v], anc)
        qc.x([b0_u, b0_v])
        
        # Case (3,0): b0_u AND b1_u AND NOT b0_v AND NOT b1_v
        qc.x([b1_v, b0_v])
        qc.mcx([b0_u, b1_u, b0_v, b1_v], anc)
        qc.x([b1_v, b0_v])
        
        # Case (3,3): b0_u AND b1_u AND b0_v AND b1_v
        qc.mcx([b0_u, b1_u, b0_v, b1_v], anc)
    
    # Compute same_color for each edge
    for edge_idx, (u, v) in enumerate(edges):
        b0_u, b1_u = get_vertex_qubits(u)
        b0_v, b1_v = get_vertex_qubits(v)
        compute_same_color_into_anc(b0_u, b1_u, b0_v, b1_v, edge_ancillas[edge_idx])
    
    # Compute valid_ancilla = NOT(mono[0] OR mono[1] OR mono[2] OR mono[3])
    qc.x(edge_ancillas)
    qc.mcx(edge_ancillas, valid_ancilla)
    qc.x(edge_ancillas)
    
    # Apply Z phase to valid colorings
    qc.z(valid_ancilla)
    
    # Uncompute valid_ancilla
    qc.x(edge_ancillas)
    qc.mcx(edge_ancillas, valid_ancilla)
    qc.x(edge_ancillas)
    
    # Uncompute edge_ancillas
    for edge_idx, (u, v) in enumerate(edges):
        b0_u, b1_u = get_vertex_qubits(u)
        b0_v, b1_v = get_vertex_qubits(v)
        compute_same_color_into_anc(b0_u, b1_u, b0_v, b1_v, edge_ancillas[edge_idx])
