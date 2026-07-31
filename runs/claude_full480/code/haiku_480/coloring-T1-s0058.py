from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [
        ([problem_qubits[0], problem_qubits[1]], [problem_qubits[2], problem_qubits[3]]),  # (0,1)
        ([problem_qubits[0], problem_qubits[1]], [problem_qubits[6], problem_qubits[7]]),  # (0,3)
        ([problem_qubits[2], problem_qubits[3]], [problem_qubits[4], problem_qubits[5]]),  # (1,2)
        ([problem_qubits[4], problem_qubits[5]], [problem_qubits[6], problem_qubits[7]]),  # (2,3)
    ]
    
    anc_invalid = ancilla_qubits[:4]
    anc_overall = ancilla_qubits[4]
    
    # Compute invalid flag for each edge
    for edge_idx, (u_qubits, v_qubits) in enumerate(edges):
        b0_u, b1_u = u_qubits
        b0_v, b1_v = v_qubits
        anc = anc_invalid[edge_idx]
        
        # Color 0 (codes 0,3): both b0=b1
        qc.mcx([b0_u, b1_u, b0_v, b1_v], anc)
        qc.x(b0_v); qc.x(b1_v)
        qc.mcx([b0_u, b1_u, b0_v, b1_v], anc)
        qc.x(b0_v); qc.x(b1_v)
        qc.x(b0_u); qc.x(b1_u)
        qc.mcx([b0_u, b1_u, b0_v, b1_v], anc)
        qc.x(b0_u); qc.x(b1_u)
        qc.x(b0_u); qc.x(b1_u); qc.x(b0_v); qc.x(b1_v)
        qc.mcx([b0_u, b1_u, b0_v, b1_v], anc)
        qc.x(b0_u); qc.x(b1_u); qc.x(b0_v); qc.x(b1_v)
        
        # Color 1 (code 1,1): both (1,0)
        qc.x(b1_u); qc.x(b1_v)
        qc.mcx([b0_u, b1_u, b0_v, b1_v], anc)
        qc.x(b1_u); qc.x(b1_v)
        
        # Color 2 (code 2,2): both (0,1)
        qc.x(b0_u); qc.x(b0_v)
        qc.mcx([b0_u, b1_u, b0_v, b1_v], anc)
        qc.x(b0_u); qc.x(b0_v)
    
    # Compute all_valid = NOT(any invalid)
    qc.x(anc_overall)
    for invalid_anc in anc_invalid:
        qc.cx(invalid_anc, anc_overall)
    
    qc.z(anc_overall)
    
    # Uncompute
    for invalid_anc in anc_invalid:
        qc.cx(invalid_anc, anc_overall)
    qc.x(anc_overall)
    
    for edge_idx in range(len(edges)-1, -1, -1):
        u_qubits, v_qubits = edges[edge_idx]
        b0_u, b1_u = u_qubits
        b0_v, b1_v = v_qubits
        anc = anc_invalid[edge_idx]
        
        qc.x(b0_u); qc.x(b0_v)
        qc.mcx([b0_u, b1_u, b0_v, b1_v], anc)
        qc.x(b0_u); qc.x(b0_v)
        
        qc.x(b1_u); qc.x(b1_v)
        qc.mcx([b0_u, b1_u, b0_v, b1_v], anc)
        qc.x(b1_u); qc.x(b1_v)
        
        qc.x(b0_u); qc.x(b1_u); qc.x(b0_v); qc.x(b1_v)
        qc.mcx([b0_u, b1_u, b0_v, b1_v], anc)
        qc.x(b0_u); qc.x(b1_u); qc.x(b0_v); qc.x(b1_v)
        
        qc.x(b0_u); qc.x(b1_u)
        qc.mcx([b0_u, b1_u, b0_v, b1_v], anc)
        qc.x(b0_u); qc.x(b1_u)
        
        qc.x(b0_v); qc.x(b1_v)
        qc.mcx([b0_u, b1_u, b0_v, b1_v], anc)
        qc.x(b0_v); qc.x(b1_v)
        
        qc.mcx([b0_u, b1_u, b0_v, b1_v], anc)
