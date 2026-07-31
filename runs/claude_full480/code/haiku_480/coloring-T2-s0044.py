from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    """
    Grover phase oracle for 3-coloring the given graph.
    Applies phase -1 to states where all edges connect different colors.
    """
    edges = [(0, 2), (0, 3), (0, 4), (1, 2), (1, 4), (3, 4)]
    
    def get_color_qubits(v):
        # Vertex v: low bit = problem_qubits[2v], high bit = problem_qubits[2v+1]
        return problem_qubits[2*v], problem_qubits[2*v + 1]
    
    # Compute violation flag (same color) for each edge into ancillas[0:6]
    for edge_idx, (u, v) in enumerate(edges):
        b0_u, b1_u = get_color_qubits(u)
        b0_v, b1_v = get_color_qubits(v)
        result = ancilla_qubits[edge_idx]
        scratch = ancilla_qubits[6]
        
        # same_color = (b0_u==b0_v AND b1_u==b1_v) OR (b0_u!=b0_v AND b1_u!=b1_v AND b0_u==b1_u)
        # Term 1: (XNOR(b0_u,b0_v) AND XNOR(b1_u,b1_v))
        
        # Compute: (b0_u XOR b0_v) into scratch
        qc.cx(b0_u, scratch)
        qc.cx(b0_v, scratch)
        qc.x(scratch)  # scratch = XNOR(b0_u, b0_v)
        
        # Compute: (b1_u XOR b1_v) into result
        qc.cx(b1_u, result)
        qc.cx(b1_v, result)
        qc.x(result)  # result = XNOR(b1_u, b1_v)
        
        # Term 1: scratch AND result -> scratch
        qc.ccx(result, scratch, scratch)
        # Now scratch holds term1 (XNOR(b0_u,b0_v) AND XNOR(b1_u,b1_v))
        
        # Reset result for term 2
        qc.x(result)
        qc.cx(b1_u, result)
        qc.cx(b1_v, result)
        
        # Term 2: (XOR(b0_u,b0_v) AND XOR(b1_u,b1_v) AND XNOR(b0_u,b1_u))
        # Compute: (b0_u XOR b0_v) into result
        qc.cx(b0_u, result)
        qc.cx(b0_v, result)
        
        # Compute: (b1_u XOR b1_v) into scratch, then AND with result
        qc.cx(b1_u, scratch)
        qc.cx(b1_v, scratch)
        qc.ccx(result, scratch, result)
        # Now result holds (XOR(b0_u,b0_v) AND XOR(b1_u,b1_v))
        
        # AND with (XNOR(b0_u,b1_u))
        qc.cx(b0_u, scratch)
        qc.cx(b1_u, scratch)
        qc.x(scratch)  # scratch = XNOR(b0_u, b1_u)
        qc.ccx(result, scratch, result)
        # result now holds term2
        
        # OR term1 and term2 for violation flag
        # First uncompute scratch to restore term1
        qc.cx(b0_u, scratch)
        qc.cx(b1_u, scratch)
        qc.x(scratch)
        qc.cx(b1_u, scratch)
        qc.cx(b1_v, scratch)
        qc.cx(b0_u, scratch)
        qc.cx(b0_v, scratch)
        qc.x(scratch)
        
        # Now scratch = term1, result = term2
        # Compute: term1 OR term2 into result using result = result OR scratch
        qc.x(scratch)
        qc.x(result)
        qc.ccx(scratch, result, result)
        qc.x(result)
        qc.x(scratch)
        # result now holds violation flag for this edge (same color)
        
        # Clean up scratch
        qc.cx(b0_u, scratch)
        qc.cx(b0_v, scratch)
        qc.x(scratch)
        qc.cx(b1_u, scratch)
        qc.cx(b1_v, scratch)
        qc.x(scratch)
    
    # Accumulate violations: any_violation = violations[0] OR violations[1] OR ... OR violations[5]
    any_violation = ancilla_qubits[6]
    for i in range(6):
        qc.x(any_violation)
        qc.x(ancilla_qubits[i])
        qc.ccx(any_violation, ancilla_qubits[i], any_violation)
        qc.x(ancilla_qubits[i])
        qc.x(any_violation)
    
    # Apply phase -1 if NO violations (any_violation == 0)
    # Use X-CZ-X to apply Z controlled by NOT any_violation
    qc.x(any_violation)
    qc.z(any_violation)
    qc.x(any_violation)
    
    # Uncompute: reverse order of operations
    for i in range(5, -1, -1):
        qc.x(any_violation)
        qc.x(ancilla_qubits[i])
        qc.ccx(any_violation, ancilla_qubits[i], any_violation)
        qc.x(ancilla_qubits[i])
        qc.x(any_violation)
    
    # Uncompute violation flags (in reverse order)
    for edge_idx in range(5, -1, -1):
        u, v = edges[edge_idx]
        b0_u, b1_u = get_color_qubits(u)
        b0_v, b1_v = get_color_qubits(v)
        scratch = ancilla_qubits[6]
        result = ancilla_qubits[edge_idx]
        
        qc.x(scratch)
        qc.cx(b1_u, scratch)
        qc.cx(b1_v, scratch)
        qc.cx(b0_u, scratch)
        qc.cx(b0_v, scratch)
        qc.x(scratch)
        
        qc.x(result)
        qc.x(scratch)
        qc.ccx(any_violation, result, result)
        qc.x(scratch)
        qc.x(result)
