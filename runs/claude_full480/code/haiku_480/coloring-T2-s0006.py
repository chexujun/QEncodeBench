from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 1), (0, 3), (0, 4), (1, 2), (1, 3), (2, 3), (2, 4)]
    
    # Allocate ancillas: one result register, rest for computations
    result = ancilla_qubits[0]
    qc.x(result)  # Initialize to |1⟩
    
    # For each edge, compute whether colors differ
    for idx, (u, v) in enumerate(edges):
        # Get color code qubits for vertices u and v
        u0, u1 = problem_qubits[2*u], problem_qubits[2*u+1]
        v0, v1 = problem_qubits[2*v], problem_qubits[2*v+1]
        
        # Temporary ancillas for this edge
        temp_base = 1 + idx
        p_u = ancilla_qubits[temp_base % len(ancilla_qubits)]
        p_v = ancilla_qubits[(temp_base + 1) % len(ancilla_qubits)]
        
        # Compute parity: p_u = u0 XOR u1
        qc.cx(u0, p_u)
        qc.cx(u1, p_u)
        
        # Compute parity: p_v = v0 XOR v1
        qc.cx(v0, p_v)
        qc.cx(v1, p_v)
        
        # same_color = (p_u == 0 AND p_v == 0) OR (p_u == 1 AND p_v == 1 AND u == v)
        # different_color = NOT same_color
        
        # Check case 1: both parities 0 (code in {00, 11} for each)
        same_flag = ancilla_qubits[(temp_base + 2) % len(ancilla_qubits)]
        qc.x(p_u)
        qc.x(p_v)
        qc.mcx([p_u, p_v], same_flag)
        qc.x(p_u)
        qc.x(p_v)
        
        # Check case 2: both parities 1 AND codes equal
        eq_flag = ancilla_qubits[(temp_base + 3) % len(ancilla_qubits)]
        
        # u0 == v0 AND u1 == v1: compute using XOR then negate
        temp_xor0 = ancilla_qubits[(temp_base + 4) % len(ancilla_qubits)]
        temp_xor1 = ancilla_qubits[(temp_base + 5) % len(ancilla_qubits)]
        
        qc.cx(u0, temp_xor0)
        qc.cx(v0, temp_xor0)
        qc.x(temp_xor0)  # Invert to get equality
        
        qc.cx(u1, temp_xor1)
        qc.cx(v1, temp_xor1)
        qc.x(temp_xor1)
        
        # Case 2: p_u AND p_v AND (u0==v0) AND (u1==v1)
        qc.mcx([p_u, p_v, temp_xor0, temp_xor1], eq_flag)
        
        # OR the two cases: same_flag = same_flag OR eq_flag
        # Implement OR as: NOT ((NOT a) AND (NOT b))
        temp_or = ancilla_qubits[(temp_base + 6) % len(ancilla_qubits)]
        qc.x(same_flag)
        qc.x(eq_flag)
        qc.mcx([same_flag, eq_flag], temp_or)
        qc.x(same_flag)
        qc.x(eq_flag)
        qc.x(temp_or)
        
        # Now same_flag OR eq_flag is in temp_or
        qc.cx(temp_or, same_flag)
        qc.x(temp_or)
        
        # same_flag now contains (same_color)
        # Invert to get different_color
        qc.x(same_flag)
        
        # AND result with different_color using controlled X
        # result = result AND different_color
        qc.mcx([result, same_flag], ancilla_qubits[(temp_base + 7) % len(ancilla_qubits)])
        qc.mcx([ancilla_qubits[(temp_base + 7) % len(ancilla_qubits)], same_flag], result)
        
        # Uncompute temporaries
        qc.x(temp_or)
        qc.cx(u1, temp_xor1)
        qc.cx(v1, temp_xor1)
        qc.cx(u0, temp_xor0)
        qc.cx(v0, temp_xor0)
        qc.cx(u1, p_u)
        qc.cx(u0, p_u)
        qc.cx(v1, p_v)
        qc.cx(v0, p_v)
    
    # Apply phase flip to result qubit
    qc.z(result)
    
    # Uncompute result back to |0⟩
    qc.x(result)
