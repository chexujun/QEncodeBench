from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    edges = [(0,1), (0,2), (0,4), (1,2), (1,3), (1,4), (2,3), (3,4)]
    
    result_anc = ancilla_qubits[0]
    same_color_anc = ancilla_qubits[1]
    temp_and = ancilla_qubits[2]
    
    # Initialize: result_anc = 1 (AND accumulator starts at identity)
    qc.x(result_anc)
    
    # Compute phase: AND of all edge validities
    for u, v in edges:
        u0, u1 = problem_qubits[2*u], problem_qubits[2*u+1]
        v0, v1 = problem_qubits[2*v], problem_qubits[2*v+1]
        
        # Compute same_color: colors are same iff one of these conditions holds:
        # (00,00), (00,11), (01,01), (10,10), (11,00), (11,11)
        
        # Condition 1: both 00
        qc.x(u0)
        qc.x(u1)
        qc.x(v0)
        qc.x(v1)
        qc.mcx([u0, u1, v0, v1], same_color_anc, mode='basic')
        qc.x(u0)
        qc.x(u1)
        qc.x(v0)
        qc.x(v1)
        
        # Condition 2: (00,11)
        qc.x(u0)
        qc.x(u1)
        qc.mcx([u0, u1, v0, v1], same_color_anc, mode='basic')
        qc.x(u0)
        qc.x(u1)
        
        # Condition 3: both 01
        qc.x(u1)
        qc.x(v1)
        qc.mcx([u0, u1, v0, v1], same_color_anc, mode='basic')
        qc.x(u1)
        qc.x(v1)
        
        # Condition 4: both 10
        qc.x(u0)
        qc.x(v0)
        qc.mcx([u0, u1, v0, v1], same_color_anc, mode='basic')
        qc.x(u0)
        qc.x(v0)
        
        # Condition 5: (11,00)
        qc.x(v0)
        qc.x(v1)
        qc.mcx([u0, u1, v0, v1], same_color_anc, mode='basic')
        qc.x(v0)
        qc.x(v1)
        
        # Condition 6: both 11
        qc.mcx([u0, u1, v0, v1], same_color_anc, mode='basic')
        
        # Accumulate: result = result AND (NOT same_color)
        qc.ccx(result_anc, same_color_anc, temp_and)
        qc.cx(temp_and, result_anc)
        qc.ccx(result_anc, same_color_anc, temp_and)
        
        # Uncompute same_color (reverse all 6 conditions)
        qc.mcx([u0, u1, v0, v1], same_color_anc, mode='basic')
        
        qc.x(v0)
        qc.x(v1)
        qc.mcx([u0, u1, v0, v1], same_color_anc, mode='basic')
        qc.x(v0)
        qc.x(v1)
        
        qc.x(u0)
        qc.x(v0)
        qc.mcx([u0, u1, v0, v1], same_color_anc, mode='basic')
        qc.x(u0)
        qc.x(v0)
        
        qc.x(u1)
        qc.x(v1)
        qc.mcx([u0, u1, v0, v1], same_color_anc, mode='basic')
        qc.x(u1)
        qc.x(v1)
        
        qc.x(u0)
        qc.x(u1)
        qc.mcx([u0, u1, v0, v1], same_color_anc, mode='basic')
        qc.x(u0)
        qc.x(u1)
        
        qc.x(u0)
        qc.x(u1)
        qc.x(v0)
        qc.x(v1)
        qc.mcx([u0, u1, v0, v1], same_color_anc, mode='basic')
        qc.x(u0)
        qc.x(u1)
        qc.x(v0)
        qc.x(v1)
    
    # Apply phase to mark valid colorings
    qc.z(result_anc)
    
    # Uncompute phase in reverse
    for u, v in reversed(edges):
        u0, u1 = problem_qubits[2*u], problem_qubits[2*u+1]
        v0, v1 = problem_qubits[2*v], problem_qubits[2*v+1]
        
        # Recompute same_color (uncompute our uncompute)
        qc.x(u0)
        qc.x(u1)
        qc.x(v0)
        qc.x(v1)
        qc.mcx([u0, u1, v0, v1], same_color_anc, mode='basic')
        qc.x(u0)
        qc.x(u1)
        qc.x(v0)
        qc.x(v1)
        
        qc.x(u0)
        qc.x(u1)
        qc.mcx([u0, u1, v0, v1], same_color_anc, mode='basic')
        qc.x(u0)
        qc.x(u1)
        
        qc.x(u1)
        qc.x(v1)
        qc.mcx([u0, u1, v0, v1], same_color_anc, mode='basic')
        qc.x(u1)
        qc.x(v1)
        
        qc.x(u0)
        qc.x(v0)
        qc.mcx([u0, u1, v0, v1], same_color_anc, mode='basic')
        qc.x(u0)
        qc.x(v0)
        
        qc.x(v0)
        qc.x(v1)
        qc.mcx([u0, u1, v0, v1], same_color_anc, mode='basic')
        qc.x(v0)
        qc.x(v1)
        
        qc.mcx([u0, u1, v0, v1], same_color_anc, mode='basic')
        
        # Reverse accumulation
        qc.ccx(result_anc, same_color_anc, temp_and)
        qc.cx(temp_and, result_anc)
        qc.ccx(result_anc, same_color_anc, temp_and)
    
    # Uncompute initialization
    qc.x(result_anc)
