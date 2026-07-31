from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    """
    Grover oracle for graph 3-coloring on a 4-vertex, 5-edge graph.
    Applies phase -1 to states where all edges connect vertices of different colors.
    """
    
    # Vertex color encodings: vertex v uses problem_qubits[2v:2v+2] (b0, b1)
    # Color decoding: c = b0 + 2*b1 -> {0→0, 1→1, 2→2, 3→0}
    # Two colors are same iff:
    #   (both codes in {00,11}) OR (codes identical)
    #   i.e., (NOT(b_u0 XOR b_u1) AND NOT(b_v0 XOR b_v1)) OR (NOT(b_u0 XOR b_v0) AND NOT(b_u1 XOR b_v1))
    
    edges = [(0, 1), (0, 2), (0, 3), (1, 2), (2, 3)]
    
    # Ancilla allocation: 5 for edges, 1 for combining
    edge_ancillas = ancilla_qubits[:5]
    combine_ancilla = ancilla_qubits[5]
    
    # Compute "same color" flag for each edge into its ancilla
    for i, (u, v) in enumerate(edges):
        compute_same_color(qc, problem_qubits, u, v, edge_ancillas[i])
    
    # XOR all edge flags into combine_ancilla
    # Result: combine_ancilla = 1 iff odd number of edges have same color
    for i in range(5):
        qc.cx(edge_ancillas[i], combine_ancilla)
    
    # Apply conditional phase: Z on combine_ancilla when it represents "all edges different"
    # Since XOR of five 0s is 0, we want phase when combine_ancilla = 0
    # Implement: X, Z, X (to flip, phase-flip, flip back)
    qc.x(combine_ancilla)
    qc.z(combine_ancilla)
    qc.x(combine_ancilla)
    
    # Uncompute XOR
    for i in range(4, -1, -1):
        qc.cx(edge_ancillas[i], combine_ancilla)
    
    # Uncompute edge flags (mirror)
    for i in range(4, -1, -1):
        u, v = edges[i]
        compute_same_color(qc, problem_qubits, u, v, edge_ancillas[i])


def compute_same_color(qc: QuantumCircuit, problem_qubits: list[int],
                       u: int, v: int, ancilla: int) -> None:
    """
    Compute whether vertices u and v have the same color.
    Sets ancilla to |1> if same color, |0> if different.
    """
    u_b0, u_b1 = problem_qubits[2*u], problem_qubits[2*u + 1]
    v_b0, v_b1 = problem_qubits[2*v], problem_qubits[2*v + 1]
    
    # Condition: (u and v both in {00,11}) OR (identical codes)
    # = (u_b0 XNOR u_b1 AND v_b0 XNOR v_b1) OR (u_b0 XNOR v_b0 AND u_b1 XNOR v_b1)
    
    # Compute using Toffoli gates and ancilla manipulation
    # Temp: use ancilla as accumulator
    
    # Case 1: Both in {00,11} (bits equal within each vertex)
    # This is true when (u_b0==u_b1) AND (v_b0==v_b1)
    # Implement: CCX(NOT u_b0, NOT u_b1, ancilla) for u_b0=u_b1=0
    #            CCX(u_b0, u_b1, ancilla) for u_b0=u_b1=1
    
    qc.cx(u_b0, u_b1)  # Temp XOR in u_b1
    qc.cx(v_b0, v_b1)  # Temp XOR in v_b1
    
    # Now u_b1 contains (u_b0 XOR u_b1), v_b1 contains (v_b0 XOR v_b1)
    # Both are 0 iff both vertices in {00,11}
    qc.mcx([u_b1, v_b1], ancilla, mode='noancilla')  # Flip ancilla if both XORs are 0
    
    # Undo the XORs in place
    qc.cx(v_b0, v_b1)
    qc.cx(u_b0, u_b1)
    
    # Case 2: Identical codes (all bits match)
    # This is (u_b0==v_b0) AND (u_b1==v_b1)
    # Equivalently, (u_b0 XNOR v_b0) AND (u_b1 XNOR v_b1)
    
    qc.cx(u_b0, v_b0)  # Temp XOR in v_b0
    qc.cx(u_b1, v_b1)  # Temp XOR in v_b1
    
    # Now v_b0 and v_b1 each contain XORs; both 0 iff codes identical
    qc.mcx([v_b0, v_b1], ancilla, mode='noancilla')  # Flip ancilla if both XORs are 0
    
    # Undo the XORs in place
    qc.cx(u_b1, v_b1)
    qc.cx(u_b0, v_b0)
