from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0,1), (0,4), (1,2), (2,3), (3,4)]
    
    # Ancilla allocation: one per edge + one for final AND result
    same_color = ancilla_qubits[0:5]
    result_ancilla = ancilla_qubits[5]
    
    # Compute same_color for each edge
    for idx, (u, v) in enumerate(edges):
        b0u, b1u = problem_qubits[2*u], problem_qubits[2*u+1]
        b0v, b1v = problem_qubits[2*v], problem_qubits[2*v+1]
        
        # same_color[idx] = 1 iff vertices u,v decode to same color
        # Decoding: 00->0, 01->1, 10->2, 11->0
        # Same color when both are: (00,00) or (01,01) or (10,10) or (11,11)
        
        for bits in [[0,0,0,0], [0,1,0,1], [1,0,1,0], [1,1,1,1]]:
            # Check if (b0u,b1u,b0v,b1v) matches bits
            # If so, apply mcx to flip same_color[idx]
            
            controls = []
            flipped = []
            
            if bits[0] == 0:
                qc.x(b0u)
                flipped.append(b0u)
            controls.append(b0u)
            
            if bits[1] == 0:
                qc.x(b1u)
                flipped.append(b1u)
            controls.append(b1u)
            
            if bits[2] == 0:
                qc.x(b0v)
                flipped.append(b0v)
            controls.append(b0v)
            
            if bits[3] == 0:
                qc.x(b1v)
                flipped.append(b1v)
            controls.append(b1v)
            
            # Apply mcx: flip same_color[idx] if all controls are |1>
            qc.mcx(controls, same_color[idx])
            
            # Flip back the controls
            for q in flipped:
                qc.x(q)
    
    # Flip all same_color to get NOT same_color (all edges satisfy constraint)
    for s in same_color:
        qc.x(s)
    
    # Compute AND of all (NOT same_color) into result_ancilla
    qc.mcx(same_color, result_ancilla)
    
    # Apply phase (-1) to result states
    qc.z(result_ancilla)
    
    # Uncompute AND
    qc.mcx(same_color, result_ancilla)
    
    # Flip same_color back to original values
    for s in same_color:
        qc.x(s)
    
    # Uncompute same_color (reverse order, reverse gate sequence)
    for idx in range(len(edges) - 1, -1, -1):
        u, v = edges[idx]
        b0u, b1u = problem_qubits[2*u], problem_qubits[2*u+1]
        b0v, b1v = problem_qubits[2*v], problem_qubits[2*v+1]
        
        for bits in [[1,1,1,1], [1,0,1,0], [0,1,0,1], [0,0,0,0]]:
            controls = []
            flipped = []
            
            if bits[0] == 0:
                qc.x(b0u)
                flipped.append(b0u)
            controls.append(b0u)
            
            if bits[1] == 0:
                qc.x(b1u)
                flipped.append(b1u)
            controls.append(b1u)
            
            if bits[2] == 0:
                qc.x(b0v)
                flipped.append(b0v)
            controls.append(b0v)
            
            if bits[3] == 0:
                qc.x(b1v)
                flipped.append(b1v)
            controls.append(b1v)
            
            qc.mcx(controls, same_color[idx])
            
            for q in flipped:
                qc.x(q)
