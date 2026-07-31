from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 2), (0, 3), (1, 3), (2, 3)]
    same_color_states = [0, 3, 5, 10, 12, 15]
    
    def get_edge_qubits(u, v):
        return [problem_qubits[2*u], problem_qubits[2*u+1],
                problem_qubits[2*v], problem_qubits[2*v+1]]
    
    # Compute monochromatic flag for each edge (1 if same color, 0 otherwise)
    for edge_idx, (u, v) in enumerate(edges):
        edge_qubits = get_edge_qubits(u, v)
        
        # For each 4-qubit state that represents same color, set the ancilla
        for state in same_color_states:
            # Flip qubits that should be 0 in the target state
            for bit_idx, qbit in enumerate(edge_qubits):
                if not (state & (1 << bit_idx)):
                    qc.x(qbit)
            
            # MCT: sets ancilla if all controls are 1 (i.e., state matches)
            qc.mct(edge_qubits, ancilla_qubits[edge_idx])
            
            # Flip back
            for bit_idx, qbit in enumerate(edge_qubits):
                if not (state & (1 << bit_idx)):
                    qc.x(qbit)
    
    # Compute all_good_flag = NOT(mono_e0) AND NOT(mono_e1) AND NOT(mono_e2) AND NOT(mono_e3)
    # This is 1 when all edges are properly colored (f(x)=1)
    for i in range(4):
        qc.x(ancilla_qubits[i])
    
    qc.mct(ancilla_qubits[:4], ancilla_qubits[4])
    
    # Apply phase -1 when all edges are properly colored
    qc.z(ancilla_qubits[4])
    
    # Uncompute all_good_flag
    qc.mct(ancilla_qubits[:4], ancilla_qubits[4])
    
    for i in range(4):
        qc.x(ancilla_qubits[i])
    
    # Uncompute monochromatic flags (reverse order)
    for edge_idx in range(3, -1, -1):
        u, v = edges[edge_idx]
        edge_qubits = get_edge_qubits(u, v)
        
        for state in reversed(same_color_states):
            for bit_idx, qbit in enumerate(edge_qubits):
                if not (state & (1 << bit_idx)):
                    qc.x(qbit)
            
            qc.mct(edge_qubits, ancilla_qubits[edge_idx])
            
            for bit_idx, qbit in enumerate(edge_qubits):
                if not (state & (1 << bit_idx)):
                    qc.x(qbit)
