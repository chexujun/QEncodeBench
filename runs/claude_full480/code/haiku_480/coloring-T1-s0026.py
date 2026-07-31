from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 2), (0, 3), (1, 2)]
    
    # Compute which edges are satisfied (colors are different)
    for i, (edge_u, edge_v) in enumerate(edges):
        u_b0 = problem_qubits[2 * edge_u]
        u_b1 = problem_qubits[2 * edge_u + 1]
        v_b0 = problem_qubits[2 * edge_v]
        v_b1 = problem_qubits[2 * edge_v + 1]
        
        # Initialize ancilla to 1 (assume satisfied)
        qc.x(ancilla_qubits[i])
        
        # List of (b0_u, b1_u, b0_v, b1_v) combinations where colors are the same
        same_color_cases = [
            (0, 0, 0, 0),
            (0, 0, 1, 1),
            (0, 1, 0, 1),
            (1, 0, 1, 0),
            (1, 1, 0, 0),
            (1, 1, 1, 1),
        ]
        
        for (b0_u_val, b1_u_val, b0_v_val, b1_v_val) in same_color_cases:
            if b0_u_val == 0:
                qc.x(u_b0)
            if b1_u_val == 0:
                qc.x(u_b1)
            if b0_v_val == 0:
                qc.x(v_b0)
            if b1_v_val == 0:
                qc.x(v_b1)
            
            qc.mcx([u_b0, u_b1, v_b0, v_b1], ancilla_qubits[i])
            
            if b0_u_val == 0:
                qc.x(u_b0)
            if b1_u_val == 0:
                qc.x(u_b1)
            if b0_v_val == 0:
                qc.x(v_b0)
            if b1_v_val == 0:
                qc.x(v_b1)
        
        qc.x(ancilla_qubits[i])
    
    # AND the edge flags
    qc.mcx([ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[2]], ancilla_qubits[3])
    
    # Apply phase -1 using phase kickback
    qc.h(ancilla_qubits[3])
    qc.z(ancilla_qubits[3])
    qc.h(ancilla_qubits[3])
    
    # Uncompute
    qc.mcx([ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[2]], ancilla_qubits[3])
    
    for i, (edge_u, edge_v) in enumerate(edges):
        u_b0 = problem_qubits[2 * edge_u]
        u_b1 = problem_qubits[2 * edge_u + 1]
        v_b0 = problem_qubits[2 * edge_v]
        v_b1 = problem_qubits[2 * edge_v + 1]
        
        qc.x(ancilla_qubits[i])
        
        same_color_cases = [
            (0, 0, 0, 0),
            (0, 0, 1, 1),
            (0, 1, 0, 1),
            (1, 0, 1, 0),
            (1, 1, 0, 0),
            (1, 1, 1, 1),
        ]
        
        for (b0_u_val, b1_u_val, b0_v_val, b1_v_val) in reversed(same_color_cases):
            if b0_u_val == 0:
                qc.x(u_b0)
            if b1_u_val == 0:
                qc.x(u_b1)
            if b0_v_val == 0:
                qc.x(v_b0)
            if b1_v_val == 0:
                qc.x(v_b1)
            
            qc.mcx([u_b0, u_b1, v_b0, v_b1], ancilla_qubits[i])
            
            if b0_u_val == 0:
                qc.x(u_b0)
            if b1_u_val == 0:
                qc.x(u_b1)
            if b0_v_val == 0:
                qc.x(v_b0)
            if b1_v_val == 0:
                qc.x(v_b1)
        
        qc.x(ancilla_qubits[i])
