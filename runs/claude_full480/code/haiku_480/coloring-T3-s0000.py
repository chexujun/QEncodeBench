def build_oracle(qc, problem_qubits, ancilla_qubits):
    from qiskit import QuantumCircuit
    
    # Edges in the graph
    edges = [
        (0, 1), (0, 2), (0, 3),
        (1, 2), (1, 3), (1, 4),
        (2, 4), (3, 4),
    ]
    
    def compute_edge_flag(u, v, output_anc):
        """
        Compute the 'different colors' flag for edge (u, v).
        The flag is 1 iff the two vertices have different colors.
        
        Color for vertex w: c_w = (b0_w + 2*b1_w) mod 3, where:
        - b0_w = problem_qubits[2*w]
        - b1_w = problem_qubits[2*w+1]
        
        Two vertices have different colors iff:
        (b0_u + 2*b1_u) mod 3 != (b0_v + 2*b1_v) mod 3
        
        This is equivalent to: NOT(b0_u XOR b0_v XOR b1_u XOR b1_v)
        So the flag = b0_u XOR b0_v XOR b1_u XOR b1_v
        """
        u0 = problem_qubits[2*u]
        u1 = problem_qubits[2*u+1]
        v0 = problem_qubits[2*v]
        v1 = problem_qubits[2*v+1]
        qc.cx(u0, output_anc)
        qc.cx(u1, output_anc)
        qc.cx(v0, output_anc)
        qc.cx(v1, output_anc)
    
    # === COMPUTE PHASE ===
    # We accumulate the AND of all edge flags.
    # Initialize anc[0] to |1> (neutral element for AND).
    qc.x(ancilla_qubits[0])
    
    # For each edge, compute its flag and AND it with the running result.
    for u, v in edges:
        # Compute the edge flag into anc[1]
        compute_edge_flag(u, v, ancilla_qubits[1])
        
        # AND with running result: anc[2] = anc[0] AND anc[1]
        qc.ccx(ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[2])
        
        # Uncompute the flag to restore anc[1] to |0>
        compute_edge_flag(u, v, ancilla_qubits[1])
        
        # Swap anc[0] and anc[2] so anc[0] holds the new AND result
        qc.cx(ancilla_qubits[2], ancilla_qubits[0])
        qc.cx(ancilla_qubits[0], ancilla_qubits[2])
        qc.cx(ancilla_qubits[2], ancilla_qubits[0])
    
    # === PHASE PHASE ===
    # Apply Z gate to anc[0]. This applies phase -1 when all edge flags are 1,
    # i.e., when all edges connect vertices of different colors.
    qc.z(ancilla_qubits[0])
    
    # === UNCOMPUTE PHASE ===
    # Reverse all operations in reverse order to restore ancillas to |0>.
    for u, v in reversed(edges):
        # Swap anc[0] and anc[2] back
        qc.cx(ancilla_qubits[2], ancilla_qubits[0])
        qc.cx(ancilla_qubits[0], ancilla_qubits[2])
        qc.cx(ancilla_qubits[2], ancilla_qubits[0])
        
        # Recompute the flag into anc[1]
        compute_edge_flag(u, v, ancilla_qubits[1])
        
        # Reverse the Toffoli to undo the AND
        qc.ccx(ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[2])
        
        # Uncompute the flag
        compute_edge_flag(u, v, ancilla_qubits[1])
    
    # Reverse the initial X to restore anc[0] to |0>
    qc.x(ancilla_qubits[0])
