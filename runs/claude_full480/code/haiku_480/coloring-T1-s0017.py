from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    """
    Grover phase oracle for graph coloring: marks valid 3-colorings.
    
    Vertices: 0, 1, 2, 3 with edges (0,1), (0,2), (1,3)
    Encoding: vertex i has qubits (q[2i], q[2i+1]) = (b0, b1)
    Colors: code 0,1,2,3 map to color 0,1,2,0 (surjective)
    """
    q = problem_qubits
    a = ancilla_qubits
    
    # Initialize validity flag to |1>
    # We'll flip this for each edge with same color; if all different, stays |1>
    qc.x(a[3])
    
    edges = [(0, 1), (0, 2), (1, 3)]
    
    def check_and_flip_if_same_color(u, v):
        """
        Check if vertices u,v have the same color.
        If so, flip the validity flag a[3].
        Same color iff: (u_b0==v_b0 AND u_b1==v_b1) OR (u_b0==u_b1 AND v_b0==v_b1)
        """
        u_b0, u_b1 = q[2*u], q[2*u+1]
        v_b0, v_b1 = q[2*v], q[2*v+1]
        
        # Compute u_b0 XOR v_b0 into a[0]
        qc.cx(u_b0, a[0])
        qc.cx(v_b0, a[0])
        
        # Compute u_b1 XOR v_b1 into a[1]
        qc.cx(u_b1, a[1])
        qc.cx(v_b1, a[1])
        
        # Compute u_b0 XOR u_b1 into a[2]
        qc.cx(u_b0, a[2])
        qc.cx(u_b1, a[2])
        
        # Condition 1: codes equal (a[0]==0 AND a[1]==0)
        # Flip a[3] if both a[0] and a[1] are zero
        qc.x(a[0])
        qc.x(a[1])
        qc.ccx(a[0], a[1], a[3])
        qc.x(a[1])
        qc.x(a[0])
        
        # Uncompute a[0] and a[1]
        qc.cx(v_b1, a[1])
        qc.cx(u_b1, a[1])
        
        qc.cx(v_b0, a[0])
        qc.cx(u_b0, a[0])
        
        # Compute v_b0 XOR v_b1 into a[0]
        qc.cx(v_b0, a[0])
        qc.cx(v_b1, a[0])
        
        # Condition 2: both have matching bits (a[2]==0 AND a[0]==0)
        # Flip a[3] if both are zero
        qc.x(a[2])
        qc.x(a[0])
        qc.ccx(a[2], a[0], a[3])
        qc.x(a[0])
        qc.x(a[2])
        
        # Uncompute a[0] and a[2]
        qc.cx(v_b1, a[0])
        qc.cx(v_b0, a[0])
        
        qc.cx(u_b1, a[2])
        qc.cx(u_b0, a[2])
    
    # Compute: flip a[3] for each same-colored edge
    for u, v in edges:
        check_and_flip_if_same_color(u, v)
    
    # Apply phase -1 when a[3]==1 (all edges have different colors)
    qc.z(a[3])
    
    # Uncompute by reversing all operations
    for u, v in reversed(edges):
        check_and_flip_if_same_color(u, v)
    
    # Reset a[3] to |0>
    qc.x(a[3])
