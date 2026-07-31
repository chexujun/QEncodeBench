from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    
    def compute_edge_constraint(qc, u_qubits, v_qubits, ancilla):
        b0_u, b1_u = u_qubits
        b0_v, b1_v = v_qubits
        
        # Indices where decoded colors differ
        # Index format: bit0=b0_u, bit1=b1_u, bit2=b0_v, bit3=b1_v
        # Color decoding: c in {0,1,2,3} maps to color c mod 3
        targets = [1, 2, 4, 6, 7, 8, 9, 11, 13, 14]
        
        for target in targets:
            b0_u_bit = (target >> 0) & 1
            b1_u_bit = (target >> 1) & 1
            b0_v_bit = (target >> 2) & 1
            b1_v_bit = (target >> 3) & 1
            
            # Apply X gates to qubits that should be 0 for this target
            if b0_u_bit == 0:
                qc.x(b0_u)
            if b1_u_bit == 0:
                qc.x(b1_u)
            if b0_v_bit == 0:
                qc.x(b0_v)
            if b1_v_bit == 0:
                qc.x(b1_v)
            
            # Apply 4-controlled X gate
            qc.mcx([b0_u, b1_u, b0_v, b1_v], ancilla)
            
            # Undo X gates
            if b0_u_bit == 0:
                qc.x(b0_u)
            if b1_u_bit == 0:
                qc.x(b1_u)
            if b0_v_bit == 0:
                qc.x(b0_v)
            if b1_v_bit == 0:
                qc.x(b1_v)
    
    def uncompute_edge_constraint(qc, u_qubits, v_qubits, ancilla):
        compute_edge_constraint(qc, u_qubits, v_qubits, ancilla)
    
    edges = [(0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]
    
    v_qubits = {}
    for v in range(4):
        v_qubits[v] = [problem_qubits[2*v], problem_qubits[2*v + 1]]
    
    edge_ancillas = ancilla_qubits[:5]
    combined_ancilla = ancilla_qubits[5]
    
    # Compute: for each edge, determine if colors differ
    for i, (u, v) in enumerate(edges):
        compute_edge_constraint(qc, v_qubits[u], v_qubits[v], edge_ancillas[i])
    
    # Combine results: set combined_ancilla to 1 iff all edges satisfy constraint
    qc.mcx(edge_ancillas, combined_ancilla)
    
    # Apply phase -1 when combined_ancilla is 1
    qc.z(combined_ancilla)
    
    # Uncompute
    qc.mcx(edge_ancillas, combined_ancilla)
    
    for i in range(len(edges) - 1, -1, -1):
        u, v = edges[i]
        uncompute_edge_constraint(qc, v_qubits[u], v_qubits[v], edge_ancillas[i])
