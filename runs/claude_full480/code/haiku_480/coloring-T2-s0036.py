from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 1), (0, 4), (1, 2), (2, 3), (2, 4), (3, 4)]
    
    # valid_anc will track if all edges have different colors (starts at |1>)
    valid_anc = ancilla_qubits[6]
    qc.x(valid_anc)
    
    for u, v in edges:
        u0, u1 = problem_qubits[2*u], problem_qubits[2*u+1]
        v0, v1 = problem_qubits[2*v], problem_qubits[2*v+1]
        same_anc = ancilla_qubits[0]
        
        # Compute "same_color" into same_anc via the 6 matching cases
        # Case 1: both code 0 (NOT u1, NOT u0, NOT v1, NOT v0)
        qc.x(u0)
        qc.x(u1)
        qc.x(v0)
        qc.x(v1)
        qc.mcx([u0, u1, v0, v1], same_anc)
        qc.x(v1)
        qc.x(v0)
        qc.x(u1)
        qc.x(u0)
        
        # Case 2: u=0, v=3 (NOT u1, NOT u0, v1, v0)
        qc.x(u0)
        qc.x(u1)
        qc.mcx([u0, u1, v0, v1], same_anc)
        qc.x(u1)
        qc.x(u0)
        
        # Case 3: both code 1 (NOT u1, u0, NOT v1, v0)
        qc.x(u1)
        qc.x(v1)
        qc.mcx([u0, u1, v0, v1], same_anc)
        qc.x(v1)
        qc.x(u1)
        
        # Case 4: both code 2 (u1, NOT u0, v1, NOT v0)
        qc.x(u0)
        qc.x(v0)
        qc.mcx([u0, u1, v0, v1], same_anc)
        qc.x(v0)
        qc.x(u0)
        
        # Case 5: u=3, v=0 (u1, u0, NOT v1, NOT v0)
        qc.x(v0)
        qc.x(v1)
        qc.mcx([u0, u1, v0, v1], same_anc)
        qc.x(v1)
        qc.x(v0)
        
        # Case 6: both code 3 (u1, u0, v1, v0)
        qc.mcx([u0, u1, v0, v1], same_anc)
        
        # Flip to get "different_color"
        qc.x(same_anc)
        
        # AND with valid_anc: valid_anc &= different_color
        qc.mcx([same_anc, valid_anc], valid_anc)
        
        # Uncompute same_anc (reverse the 6 cases)
        qc.mcx([u0, u1, v0, v1], same_anc)
        qc.x(v1)
        qc.x(v0)
        qc.x(u1)
        qc.x(u0)
        qc.mcx([u0, u1, v0, v1], same_anc)
        qc.x(v0)
        qc.x(u0)
        qc.x(u1)
        qc.x(v1)
        qc.mcx([u0, u1, v0, v1], same_anc)
        qc.x(u1)
        qc.x(v1)
        qc.mcx([u0, u1, v0, v1], same_anc)
        qc.x(u0)
        qc.x(u1)
        qc.mcx([u0, u1, v0, v1], same_anc)
        qc.x(u1)
        qc.x(u0)
        qc.x(u0)
        qc.x(u1)
        qc.x(v0)
        qc.x(v1)
        qc.mcx([u0, u1, v0, v1], same_anc)
        qc.x(v1)
        qc.x(v0)
        qc.x(u1)
        qc.x(u0)
    
    # Apply phase to valid_anc
    qc.z(valid_anc)
    
    # Uncompute valid_anc to |0>
    qc.x(valid_anc)
