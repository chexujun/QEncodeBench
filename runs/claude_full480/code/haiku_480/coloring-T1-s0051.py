from qiskit import QuantumCircuit
from math import pi

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    
    # Map vertices to their problem qubits
    # Vertex v uses qubits [2*v] (b0, low bit) and [2*v+1] (b1, high bit)
    vertices = {}
    for v in range(5):
        vertices[v] = (problem_qubits[2*v], problem_qubits[2*v+1])
    
    # Define edges in the graph
    edges = [(0, 2), (0, 4), (1, 3), (2, 4)]
    
    # Use first 4 ancillas to store same_color flags for each edge
    same_ancillas = ancilla_qubits[:4]
    
    # Cases where two vertices have the same color.
    # These are the 6 basis states (b0_u, b1_u, b0_v, b1_v) where decode(b0_u, b1_u) == decode(b0_v, b1_v).
    # Color decoding: code c = b0 + 2*b1, color = c % 3 (with c=3 -> color 0)
    # Same color when: (both code 0 or 3) OR (both code 1) OR (both code 2)
    same_color_cases = [
        (0, 0, 0, 0),  # both color 0 (code 0)
        (0, 0, 1, 1),  # both color 0 (code 0 and 3)
        (0, 1, 0, 1),  # both color 2 (code 2)
        (1, 0, 1, 0),  # both color 1 (code 1)
        (1, 1, 0, 0),  # both color 0 (code 3 and 0)
        (1, 1, 1, 1),  # both color 0 (code 3)
    ]
    
    def compute_same_color(u, v, same_ancilla):
        """Compute into same_ancilla: 1 iff vertices u and v have same color."""
        b0_u, b1_u = vertices[u]
        b0_v, b1_v = vertices[v]
        
        for c0, c1, c2, c3 in same_color_cases:
            # Apply X to invert bits that should be 0 for this case
            if c0 == 0:
                qc.x(b0_u)
            if c1 == 0:
                qc.x(b1_u)
            if c2 == 0:
                qc.x(b0_v)
            if c3 == 0:
                qc.x(b1_v)
            
            # Multi-controlled X: flip same_ancilla iff all controls are 1 (i.e., case matches)
            qc.mcx([b0_u, b1_u, b0_v, b1_v], same_ancilla)
            
            # Uncompute: restore original qubit values
            if c0 == 0:
                qc.x(b0_u)
            if c1 == 0:
                qc.x(b1_u)
            if c2 == 0:
                qc.x(b0_v)
            if c3 == 0:
                qc.x(b1_v)
    
    # Compute: determine same_color for each edge
    for i, (u, v) in enumerate(edges):
        compute_same_color(u, v, same_ancillas[i])
    
    # Phase: apply -1 phase iff all edges have different colors (i.e., all same_color flags are 0)
    # Multi-controlled phase gate activates when all controls are 1, so flip ancillas first
    for a in same_ancillas:
        qc.x(a)
    
    qc.mcp(pi, same_ancillas, problem_qubits[0])
    
    for a in same_ancillas:
        qc.x(a)
    
    # Uncompute: reverse the compute step (in reverse order)
    for i in range(len(edges) - 1, -1, -1):
        u, v = edges[i]
        compute_same_color(u, v, same_ancillas[i])
