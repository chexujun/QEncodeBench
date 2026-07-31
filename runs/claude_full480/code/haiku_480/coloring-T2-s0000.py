from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 1), (0, 2), (1, 2), (1, 3), (1, 4)]
    
    # Step 1: Compute monochromatic indicator for each edge
    # For edge (u, v), compute whether their colors are the same (monochromatic)
    # This is true iff (u_code, v_code) match one of these patterns:
    # (0,0), (1,1), (2,2), (3,0), (0,3), (3,3)
    for edge_idx, (u, v) in enumerate(edges):
        u0, u1 = problem_qubits[2*u], problem_qubits[2*u+1]
        v0, v1 = problem_qubits[2*v], problem_qubits[2*v+1]
        a = ancilla_qubits[edge_idx]
        
        # Pattern 1: (0,0)-(0,0) — all bits are 0
        qc.x(u1)
        qc.x(u0)
        qc.x(v1)
        qc.x(v0)
        qc.mcx([u1, u0, v1, v0], a)
        qc.x(v0)
        qc.x(v1)
        qc.x(u0)
        qc.x(u1)
        
        # Pattern 2: (0,1)-(0,1)
        qc.x(u1)
        qc.x(v1)
        qc.mcx([u1, u0, v1, v0], a)
        qc.x(v1)
        qc.x(u1)
        
        # Pattern 3: (1,0)-(1,0)
        qc.x(u0)
        qc.x(v0)
        qc.mcx([u1, u0, v1, v0], a)
        qc.x(v0)
        qc.x(u0)
        
        # Pattern 4: (1,1)-(0,0)
        qc.x(v1)
        qc.x(v0)
        qc.mcx([u1, u0, v1, v0], a)
        qc.x(v0)
        qc.x(v1)
        
        # Pattern 5: (0,0)-(1,1)
        qc.x(u1)
        qc.x(u0)
        qc.mcx([u1, u0, v1, v0], a)
        qc.x(u0)
        qc.x(u1)
        
        # Pattern 6: (1,1)-(1,1) — all bits are 1
        qc.mcx([u1, u0, v1, v0], a)
    
    # Step 2: Compute valid = AND(NOT ancilla[i] for i in 0..4)
    # This is true iff no edge is monochromatic
    valid = ancilla_qubits[5]
    qc.x(valid)  # Initialize valid to |1>
    
    # Flip all ancillas to negate them
    for i in range(5):
        qc.x(ancilla_qubits[i])
    
    # Check if all negated ancillas are 1 (i.e., all originals are 0)
    qc.mcx([ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[2], 
            ancilla_qubits[3], ancilla_qubits[4]], valid)
    
    # Flip ancillas back
    for i in range(5):
        qc.x(ancilla_qubits[i])
    
    # Step 3: Apply phase if valid == 1
    qc.z(valid)
    
    # Step 4: Uncompute valid
    for i in range(5):
        qc.x(ancilla_qubits[i])
    qc.mcx([ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[2], 
            ancilla_qubits[3], ancilla_qubits[4]], valid)
    for i in range(5):
        qc.x(ancilla_qubits[i])
    qc.x(valid)
    
    # Step 5: Uncompute edge monochromatic indicators (reverse order)
    for edge_idx in range(4, -1, -1):
        u, v = edges[edge_idx]
        u0, u1 = problem_qubits[2*u], problem_qubits[2*u+1]
        v0, v1 = problem_qubits[2*v], problem_qubits[2*v+1]
        a = ancilla_qubits[edge_idx]
        
        qc.mcx([u1, u0, v1, v0], a)
        qc.x(u1)
        qc.x(u0)
        qc.mcx([u1, u0, v1, v0], a)
        qc.x(u0)
        qc.x(u1)
        qc.x(v1)
        qc.x(v0)
        qc.mcx([u1, u0, v1, v0], a)
        qc.x(v0)
        qc.x(v1)
        qc.x(u0)
        qc.x(v0)
        qc.mcx([u1, u0, v1, v0], a)
        qc.x(v0)
        qc.x(u0)
        qc.x(u1)
        qc.x(v1)
        qc.mcx([u1, u0, v1, v0], a)
        qc.x(v1)
        qc.x(u1)
        qc.x(u1)
        qc.x(u0)
        qc.x(v1)
        qc.x(v0)
        qc.mcx([u1, u0, v1, v0], a)
        qc.x(v0)
        qc.x(v1)
        qc.x(u0)
        qc.x(u1)
