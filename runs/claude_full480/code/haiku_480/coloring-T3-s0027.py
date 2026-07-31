from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0,1), (0,2), (0,4), (1,3), (1,5), (2,4), (3,4), (4,5)]
    
    # Ancilla assignment
    result_flag = ancilla_qubits[0]  # Accumulates violations (1 if any edge is monochromatic)
    temp_a = ancilla_qubits[1]
    temp_b = ancilla_qubits[2]
    temp_c = ancilla_qubits[3]
    
    # For each edge, check if it is monochromatic and accumulate violations
    for u, v in edges:
        u_b0 = problem_qubits[2*u]
        u_b1 = problem_qubits[2*u+1]
        v_b0 = problem_qubits[2*v]
        v_b1 = problem_qubits[2*v+1]
        
        # COMPUTE: Check if vertices u and v have the same color
        # Colors are same if:
        # 1. Codes are identical: (u_b0==v_b0) AND (u_b1==v_b1), OR
        # 2. u=(1,1) and v=(0,0), OR  
        # 3. u=(0,0) and v=(1,1)
        
        # Step 1: Check if codes differ
        qc.cx(u_b0, temp_a)
        qc.cx(v_b0, temp_a)
        qc.cx(u_b1, temp_b)
        qc.cx(v_b1, temp_b)
        # temp_a = 1 iff u_b0 != v_b0
        # temp_b = 1 iff u_b1 != v_b1
        
        # Combine: codes_match = NOT(temp_a OR temp_b)
        qc.cx(temp_a, temp_b)
        qc.x(temp_b)
        # temp_b = 1 iff codes are identical
        
        # Step 2: Check special case u=(1,1) and v=(0,0)
        qc.x(v_b0)
        qc.x(v_b1)
        qc.mcx([u_b0, u_b1, v_b0, v_b1], temp_c)
        qc.x(v_b0)
        qc.x(v_b1)
        # temp_c = 1 iff u=(1,1) and v=(0,0)
        
        # Step 3: Check special case u=(0,0) and v=(1,1)
        qc.x(u_b0)
        qc.x(u_b1)
        qc.mcx([u_b0, u_b1, v_b0, v_b1], temp_c)
        qc.x(u_b0)
        qc.x(u_b1)
        # temp_c = 1 iff ((u=(1,1) and v=(0,0)) OR (u=(0,0) and v=(1,1)))
        
        # same_color = temp_b OR temp_c
        qc.cx(temp_c, temp_b)
        # temp_b = 1 iff same_color
        
        # Accumulate violation: result_flag XOR= same_color
        qc.cx(temp_b, result_flag)
        
        # UNCOMPUTE: reverse all operations
        qc.cx(temp_c, temp_b)
        
        qc.x(u_b0)
        qc.x(u_b1)
        qc.mcx([u_b0, u_b1, v_b0, v_b1], temp_c)
        qc.x(u_b0)
        qc.x(u_b1)
        
        qc.x(v_b0)
        qc.x(v_b1)
        qc.mcx([u_b0, u_b1, v_b0, v_b1], temp_c)
        qc.x(v_b0)
        qc.x(v_b1)
        
        qc.x(temp_b)
        qc.cx(temp_a, temp_b)
        
        qc.cx(u_b1, temp_b)
        qc.cx(v_b1, temp_b)
        
        qc.cx(u_b0, temp_a)
        qc.cx(v_b0, temp_a)
    
    # PHASE: Apply Z gate to flip sign if no violations (result_flag = 0)
    qc.x(result_flag)
    qc.z(result_flag)
    qc.x(result_flag)
    
    # UNCOMPUTE all edges in reverse order
    for u, v in reversed(edges):
        u_b0 = problem_qubits[2*u]
        u_b1 = problem_qubits[2*u+1]
        v_b0 = problem_qubits[2*v]
        v_b1 = problem_qubits[2*v+1]
        
        qc.cx(v_b0, temp_a)
        qc.cx(u_b0, temp_a)
        
        qc.cx(v_b1, temp_b)
        qc.cx(u_b1, temp_b)
        
        qc.cx(temp_a, temp_b)
        qc.x(temp_b)
        
        qc.x(v_b0)
        qc.x(v_b1)
        qc.mcx([u_b0, u_b1, v_b0, v_b1], temp_c)
        qc.x(v_b0)
        qc.x(v_b1)
        
        qc.x(u_b0)
        qc.x(u_b1)
        qc.mcx([u_b0, u_b1, v_b0, v_b1], temp_c)
        qc.x(u_b0)
        qc.x(u_b1)
        
        qc.cx(temp_c, temp_b)
        
        qc.cx(temp_b, result_flag)
