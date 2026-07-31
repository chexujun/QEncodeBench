from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 1), (0, 2), (0, 3), (2, 3), (2, 4)]
    
    same_color_flags = ancilla_qubits[:5]
    and_result = ancilla_qubits[5]
    
    # Compute same_color flags for each edge
    for i, (u, v) in enumerate(edges):
        b0_u = problem_qubits[2*u]
        b1_u = problem_qubits[2*u + 1]
        b0_v = problem_qubits[2*v]
        b1_v = problem_qubits[2*v + 1]
        
        same_color = same_color_flags[i]
        
        # Check all 6 same-color patterns (code_u, code_v):
        # (0,0), (0,3), (1,1), (2,2), (3,0), (3,3)
        # In bits: (0,0,0,0), (0,0,1,1), (1,0,1,0), (0,1,0,1), (1,1,0,0), (1,1,1,1)
        
        # Pattern 1: (0, 0, 0, 0)
        qc.x(b0_u)
        qc.x(b1_u)
        qc.x(b0_v)
        qc.x(b1_v)
        qc.mcx([b0_u, b1_u, b0_v, b1_v], same_color)
        qc.x(b0_u)
        qc.x(b1_u)
        qc.x(b0_v)
        qc.x(b1_v)
        
        # Pattern 2: (0, 0, 1, 1)
        qc.x(b0_u)
        qc.x(b1_u)
        qc.mcx([b0_u, b1_u, b0_v, b1_v], same_color)
        qc.x(b0_u)
        qc.x(b1_u)
        
        # Pattern 3: (1, 0, 1, 0)
        qc.x(b1_u)
        qc.x(b1_v)
        qc.mcx([b0_u, b1_u, b0_v, b1_v], same_color)
        qc.x(b1_u)
        qc.x(b1_v)
        
        # Pattern 4: (0, 1, 0, 1)
        qc.x(b0_u)
        qc.x(b0_v)
        qc.mcx([b0_u, b1_u, b0_v, b1_v], same_color)
        qc.x(b0_u)
        qc.x(b0_v)
        
        # Pattern 5: (1, 1, 0, 0)
        qc.x(b0_v)
        qc.x(b1_v)
        qc.mcx([b0_u, b1_u, b0_v, b1_v], same_color)
        qc.x(b0_v)
        qc.x(b1_v)
        
        # Pattern 6: (1, 1, 1, 1)
        qc.mcx([b0_u, b1_u, b0_v, b1_v], same_color)
    
    # Negate to get different_color flags
    for i in range(5):
        qc.x(same_color_flags[i])
    
    # AND all flags and apply phase
    qc.mcx(same_color_flags, and_result)
    qc.z(and_result)
    qc.mcx(same_color_flags, and_result)
    
    # Uncompute negation
    for i in range(5):
        qc.x(same_color_flags[i])
    
    # Uncompute same_color flags (reverse order)
    for i in range(len(edges)-1, -1, -1):
        u, v = edges[i]
        b0_u = problem_qubits[2*u]
        b1_u = problem_qubits[2*u + 1]
        b0_v = problem_qubits[2*v]
        b1_v = problem_qubits[2*v + 1]
        
        same_color = same_color_flags[i]
        
        # Undo Pattern 6
        qc.mcx([b0_u, b1_u, b0_v, b1_v], same_color)
        
        # Undo Pattern 5
        qc.x(b0_v)
        qc.x(b1_v)
        qc.mcx([b0_u, b1_u, b0_v, b1_v], same_color)
        qc.x(b0_v)
        qc.x(b1_v)
        
        # Undo Pattern 4
        qc.x(b0_u)
        qc.x(b0_v)
        qc.mcx([b0_u, b1_u, b0_v, b1_v], same_color)
        qc.x(b0_u)
        qc.x(b0_v)
        
        # Undo Pattern 3
        qc.x(b1_u)
        qc.x(b1_v)
        qc.mcx([b0_u, b1_u, b0_v, b1_v], same_color)
        qc.x(b1_u)
        qc.x(b1_v)
        
        # Undo Pattern 2
        qc.x(b0_u)
        qc.x(b1_u)
        qc.mcx([b0_u, b1_u, b0_v, b1_v], same_color)
        qc.x(b0_u)
        qc.x(b1_u)
        
        # Undo Pattern 1
        qc.x(b0_u)
        qc.x(b1_u)
        qc.x(b0_v)
        qc.x(b1_v)
        qc.mcx([b0_u, b1_u, b0_v, b1_v], same_color)
        qc.x(b0_u)
        qc.x(b1_u)
        qc.x(b0_v)
        qc.x(b1_v)
