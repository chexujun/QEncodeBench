from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    """
    Graph coloring oracle for 4-vertex graph with edges (0,1), (0,3), (1,2), (1,3), (2,3).
    Color coding: 2 bits per vertex (b0, b1), color = (b0 + 2*b1) % 3.
    Applies phase -1 iff all edges connect vertices of different colors.
    """
    
    # Graph edges
    edges = [(0, 1), (0, 3), (1, 2), (1, 3), (2, 3)]
    
    def compute_edge_constraint(b0_u: int, b1_u: int, b0_v: int, b1_v: int, ancilla: int):
        """
        Compute ancilla = 1 iff colors at vertices u and v are equal.
        Checks 6 cases where colors match, using XOR accumulation
        (at most one case is true for any input, so XOR = OR).
        Then inverts to get: ancilla = 1 iff colors differ.
        """
        
        # Case 1: code(u)=(0,0) AND code(v)=(0,0) → colors (0,0)
        qc.x(b0_u)
        qc.x(b1_u)
        qc.x(b0_v)
        qc.x(b1_v)
        qc.mcx([b0_u, b1_u, b0_v, b1_v], ancilla)
        qc.x(b0_u)
        qc.x(b1_u)
        qc.x(b0_v)
        qc.x(b1_v)
        
        # Case 2: code(u)=(0,0) AND code(v)=(1,1) → colors (0,0)
        qc.x(b0_u)
        qc.x(b1_u)
        qc.mcx([b0_u, b1_u, b0_v, b1_v], ancilla)
        qc.x(b0_u)
        qc.x(b1_u)
        
        # Case 3: code(u)=(0,1) AND code(v)=(0,1) → colors (1,1)
        qc.x(b0_u)
        qc.x(b0_v)
        qc.mcx([b0_u, b1_u, b0_v, b1_v], ancilla)
        qc.x(b0_u)
        qc.x(b0_v)
        
        # Case 4: code(u)=(1,0) AND code(v)=(1,0) → colors (2,2)
        qc.x(b1_u)
        qc.x(b1_v)
        qc.mcx([b0_u, b1_u, b0_v, b1_v], ancilla)
        qc.x(b1_u)
        qc.x(b1_v)
        
        # Case 5: code(u)=(1,1) AND code(v)=(0,0) → colors (0,0)
        qc.x(b0_v)
        qc.x(b1_v)
        qc.mcx([b0_u, b1_u, b0_v, b1_v], ancilla)
        qc.x(b0_v)
        qc.x(b1_v)
        
        # Case 6: code(u)=(1,1) AND code(v)=(1,1) → colors (0,0)
        qc.mcx([b0_u, b1_u, b0_v, b1_v], ancilla)
        
        # Now ancilla = OR(all cases) = (colors are equal)
        # Invert: ancilla = (colors differ)
        qc.x(ancilla)
    
    # COMPUTE: For each edge, compute whether the constraint is satisfied
    for i, (u, v) in enumerate(edges):
        b0_u = problem_qubits[2 * u]
        b1_u = problem_qubits[2 * u + 1]
        b0_v = problem_qubits[2 * v]
        b1_v = problem_qubits[2 * v + 1]
        compute_edge_constraint(b0_u, b1_u, b0_v, b1_v, ancilla_qubits[i])
    
    # AND all edge constraints: ancilla[5] = 1 iff all edges are valid
    qc.mcx(ancilla_qubits[0:5], ancilla_qubits[5])
    
    # PHASE: Apply Z gate to ancilla[5] (applies phase -1 when ancilla[5]=1)
    qc.z(ancilla_qubits[5])
    
    # UNCOMPUTE: Reverse all compute steps
    qc.mcx(ancilla_qubits[0:5], ancilla_qubits[5])
    
    for i in reversed(range(len(edges))):
        u, v = edges[i]
        b0_u = problem_qubits[2 * u]
        b1_u = problem_qubits[2 * u + 1]
        b0_v = problem_qubits[2 * v]
        b1_v = problem_qubits[2 * v + 1]
        compute_edge_constraint(b0_u, b1_u, b0_v, b1_v, ancilla_qubits[i])
