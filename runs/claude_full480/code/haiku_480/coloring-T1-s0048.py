from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Extract problem qubits for each vertex
    b0 = [problem_qubits[2*v] for v in range(4)]
    b1 = [problem_qubits[2*v+1] for v in range(4)]
    
    # Ancilla qubits
    result, tmp1, tmp2, tmp3, tmp4 = ancilla_qubits
    
    # Initialize result accumulator to 1
    qc.x(result)
    
    edges = [(0, 1), (0, 2), (0, 3), (1, 2)]
    
    for u, v in edges:
        # Compute: different_colors(u,v) = 
        #   ((b1_u XOR b1_v) OR (b0_u XOR b0_v)) AND 
        #   ((b1_u XOR b0_u) OR (b1_v XOR b0_v))
        
        # Compute part1 = (b1_u XOR b1_v) OR (b0_u XOR b0_v)
        qc.cx(b1[u], tmp1)
        qc.cx(b1[v], tmp1)
        qc.cx(b0[u], tmp2)
        qc.cx(b0[v], tmp2)
        # Compute OR using: a OR b = a XOR b XOR (a AND b)
        qc.ccx(tmp1, tmp2, tmp3)
        qc.cx(tmp3, tmp1)
        qc.cx(tmp3, tmp2)
        qc.ccx(tmp1, tmp2, tmp3)
        # tmp1 now holds part1
        
        # Compute part2 = (b1_u XOR b0_u) OR (b1_v XOR b0_v)
        qc.cx(b0[u], tmp2)
        qc.cx(b1[v], tmp3)
        qc.cx(b0[v], tmp3)
        # Compute OR
        qc.ccx(tmp2, tmp3, tmp4)
        qc.cx(tmp4, tmp2)
        qc.cx(tmp4, tmp3)
        qc.ccx(tmp2, tmp3, tmp4)
        # tmp2 now holds part2
        
        # Compute edge_valid = part1 AND part2 into tmp3
        qc.ccx(tmp1, tmp2, tmp3)
        
        # AND result with edge_valid: result = result AND tmp3
        qc.x(tmp3)
        qc.ccx(tmp3, result, tmp4)
        qc.cx(tmp4, result)
        qc.x(tmp3)
        
        # Uncompute part2
        qc.ccx(tmp2, tmp3, tmp4)
        qc.cx(tmp4, tmp3)
        qc.cx(tmp4, tmp2)
        qc.cx(b1[v], tmp3)
        qc.cx(b0[v], tmp3)
        qc.cx(b0[u], tmp2)
        
        # Uncompute part1
        qc.ccx(tmp1, tmp2, tmp3)
        qc.cx(tmp3, tmp2)
        qc.cx(tmp3, tmp1)
        qc.cx(b0[v], tmp2)
        qc.cx(b0[u], tmp2)
        qc.cx(b1[v], tmp1)
        qc.cx(b1[u], tmp1)
    
    # Apply Z phase to result
    qc.z(result)
    
    # Uncompute result back to 0
    qc.x(result)
