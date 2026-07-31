from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    anc = ancilla_qubits
    
    # For each edge (u, v), compute whether colors differ.
    # Vertex i has 2-bit code at [2i] (low) and [2i+1] (high).
    # Colors differ iff (d_low XOR d_high) where d_j = code_u[j] XOR code_v[j].
    
    # Compute edge_01_valid: vertices 0 (bits 0,1) and 1 (bits 2,3)
    qc.cx(problem_qubits[0], anc[1])
    qc.cx(problem_qubits[2], anc[1])
    qc.cx(problem_qubits[1], anc[1])
    qc.cx(problem_qubits[3], anc[1])
    
    # Compute edge_13_valid: vertices 1 (bits 2,3) and 3 (bits 6,7)
    qc.cx(problem_qubits[2], anc[2])
    qc.cx(problem_qubits[6], anc[2])
    qc.cx(problem_qubits[3], anc[2])
    qc.cx(problem_qubits[7], anc[2])
    
    # Compute edge_23_valid: vertices 2 (bits 4,5) and 3 (bits 6,7)
    qc.cx(problem_qubits[4], anc[3])
    qc.cx(problem_qubits[6], anc[3])
    qc.cx(problem_qubits[5], anc[3])
    qc.cx(problem_qubits[7], anc[3])
    
    # Compute all_valid = anc[1] AND anc[2] AND anc[3]
    qc.mcx([anc[1], anc[2], anc[3]], anc[0])
    
    # Apply phase flip
    qc.z(anc[0])
    
    # Uncompute: reverse all_valid computation
    qc.mcx([anc[1], anc[2], anc[3]], anc[0])
    
    # Uncompute edge validities
    qc.cx(problem_qubits[4], anc[3])
    qc.cx(problem_qubits[6], anc[3])
    qc.cx(problem_qubits[5], anc[3])
    qc.cx(problem_qubits[7], anc[3])
    
    qc.cx(problem_qubits[2], anc[2])
    qc.cx(problem_qubits[6], anc[2])
    qc.cx(problem_qubits[3], anc[2])
    qc.cx(problem_qubits[7], anc[2])
    
    qc.cx(problem_qubits[0], anc[1])
    qc.cx(problem_qubits[2], anc[1])
    qc.cx(problem_qubits[1], anc[1])
    qc.cx(problem_qubits[3], anc[1])
