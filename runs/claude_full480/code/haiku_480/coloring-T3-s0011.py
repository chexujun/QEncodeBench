def build_oracle(qc, problem_qubits, ancilla_qubits):
    result = ancilla_qubits[0]
    edge_violation = ancilla_qubits[1]
    temp1 = ancilla_qubits[2]
    temp2 = ancilla_qubits[3]
    
    # Initialize result to 1 (assume all edges valid initially)
    qc.x(result)
    
    edges = [(0,1), (0,2), (1,2), (1,3), (1,4), (2,3), (2,4)]
    
    for u, v in edges:
        b0_u, b1_u = problem_qubits[2*u], problem_qubits[2*u+1]
        b0_v, b1_v = problem_qubits[2*v], problem_qubits[2*v+1]
        
        # Compute if colors match:
        # Colors match iff: (b0_u==b0_v AND b1_u==b1_v) 
        #   OR (b0_u!=b0_v AND b1_u!=b1_v AND b0_u==b1_u AND b0_v==b1_v)
        
        # temp1 = b0_u XOR b0_v (0 if equal, 1 if different)
        qc.cx(b0_u, temp1)
        qc.cx(b0_v, temp1)
        
        # temp2 = b1_u XOR b1_v (0 if equal, 1 if different)
        qc.cx(b1_u, temp2)
        qc.cx(b1_v, temp2)
        
        # Condition 1: NOT temp1 AND NOT temp2 (both codes have same bits)
        qc.x(temp1)
        qc.x(temp2)
        qc.ccx(temp1, temp2, edge_violation)
        qc.x(temp2)
        qc.x(temp1)
        
        # Condition 2: temp1 AND temp2 AND (b0_u==b1_u) AND (b0_v==b1_v)
        # Codes are opposite but both have matching b0==b1 within vertex (codes 00/11)
        qc.ccx(temp1, temp2, temp1)
        # temp1 now holds: (b0_u XOR b0_v) AND (b1_u XOR b1_v)
        
        # Check if b0_u == b1_u
        qc.cx(b0_u, temp2)
        qc.cx(b1_u, temp2)
        qc.x(temp2)
        # temp2 = NOT(b0_u XOR b1_u) = (b0_u == b1_u)
        
        qc.ccx(temp1, temp2, edge_violation)
        # edge_violation = edge_violation OR (temp1 AND temp2)
        
        qc.x(temp2)
        qc.cx(b0_u, temp2)
        qc.cx(b1_u, temp2)
        
        # Check if b0_v == b1_v
        qc.cx(b0_v, temp2)
        qc.cx(b1_v, temp2)
        qc.x(temp2)
        
        qc.ccx(temp1, temp2, edge_violation)
        # edge_violation = edge_violation OR (temp1 AND temp2 AND (b0_v==b1_v))
        
        # Uncompute temp2
        qc.x(temp2)
        qc.cx(b0_v, temp2)
        qc.cx(b1_v, temp2)
        
        # Uncompute temp1 (reverse the AND)
        qc.ccx(temp1, temp2, temp1)
        qc.cx(b1_u, temp2)
        qc.cx(b0_u, temp2)
        
        # Uncompute XOR values in temp1, temp2
        qc.cx(b1_u, temp2)
        qc.cx(b1_v, temp2)
        qc.cx(b0_u, temp1)
        qc.cx(b0_v, temp1)
        
        # Apply AND: result = result AND NOT edge_violation
        qc.ccx(result, edge_violation, result)
    
    # Apply phase when result == 1
    qc.z(result)
    
    # Uncompute in reverse order (mirror)
    for u, v in reversed(edges):
        b0_u, b1_u = problem_qubits[2*u], problem_qubits[2*u+1]
        b0_v, b1_v = problem_qubits[2*v], problem_qubits[2*v+1]
        
        qc.cx(b0_u, temp1)
        qc.cx(b0_v, temp1)
        qc.cx(b1_u, temp2)
        qc.cx(b1_v, temp2)
        
        qc.ccx(temp1, temp2, temp1)
        qc.cx(b0_u, temp2)
        qc.cx(b1_u, temp2)
        qc.x(temp2)
        qc.ccx(temp1, temp2, edge_violation)
        qc.x(temp2)
        qc.cx(b0_u, temp2)
        qc.cx(b1_u, temp2)
        qc.cx(b0_v, temp2)
        qc.cx(b1_v, temp2)
        qc.x(temp2)
        qc.ccx(temp1, temp2, edge_violation)
        qc.x(temp2)
        qc.cx(b0_v, temp2)
        qc.cx(b1_v, temp2)
        qc.ccx(temp1, temp2, temp1)
        qc.cx(b1_u, temp2)
        qc.cx(b1_v, temp2)
        qc.cx(b0_u, temp1)
        qc.cx(b0_v, temp1)
        
        qc.x(temp1)
        qc.x(temp2)
        qc.ccx(temp1, temp2, edge_violation)
        qc.x(temp2)
        qc.x(temp1)
        
        qc.ccx(result, edge_violation, result)
    
    # Uncompute result initialization
    qc.x(result)
