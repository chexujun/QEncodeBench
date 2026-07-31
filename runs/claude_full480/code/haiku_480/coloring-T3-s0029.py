def build_oracle(qc, problem_qubits, ancilla_qubits):
    from qiskit.circuit import QuantumCircuit
    
    edges = [(0,1), (0,4), (0,5), (1,3), (1,5), (2,3), (3,4), (4,5)]
    
    all_valid = ancilla_qubits[0]
    temp1 = ancilla_qubits[1]
    temp2 = ancilla_qubits[2]
    temp3 = ancilla_qubits[3]
    temp4 = ancilla_qubits[4]
    
    qc.x(all_valid)
    
    for u, v in edges:
        b0_u = problem_qubits[2*u]
        b1_u = problem_qubits[2*u + 1]
        b0_v = problem_qubits[2*v]
        b1_v = problem_qubits[2*v + 1]
        
        same_color = temp1
        
        conditions = [
            (0, 0, 0, 0),
            (0, 0, 1, 1),
            (1, 0, 1, 0),
            (0, 1, 0, 1),
            (1, 1, 0, 0),
            (1, 1, 1, 1),
        ]
        
        for b0_u_val, b1_u_val, b0_v_val, b1_v_val in conditions:
            if b0_u_val == 0:
                qc.x(b0_u)
            if b1_u_val == 0:
                qc.x(b1_u)
            if b0_v_val == 0:
                qc.x(b0_v)
            if b1_v_val == 0:
                qc.x(b1_v)
            
            qc.mcx([b0_u, b1_u, b0_v, b1_v], temp2)
            
            qc.x(same_color)
            qc.ccx(same_color, temp2, same_color)
            qc.x(same_color)
            
            qc.mcx([b0_u, b1_u, b0_v, b1_v], temp2)
            
            if b0_v_val == 0:
                qc.x(b0_v)
            if b1_v_val == 0:
                qc.x(b1_v)
            if b1_u_val == 0:
                qc.x(b1_u)
            if b0_u_val == 0:
                qc.x(b0_u)
        
        qc.ccx(same_color, all_valid, all_valid)
    
    qc.z(all_valid)
    
    for u, v in reversed(edges):
        b0_u = problem_qubits[2*u]
        b1_u = problem_qubits[2*u + 1]
        b0_v = problem_qubits[2*v]
        b1_v = problem_qubits[2*v + 1]
        
        same_color = temp1
        
        conditions = [
            (0, 0, 0, 0),
            (0, 0, 1, 1),
            (1, 0, 1, 0),
            (0, 1, 0, 1),
            (1, 1, 0, 0),
            (1, 1, 1, 1),
        ]
        
        for b0_u_val, b1_u_val, b0_v_val, b1_v_val in conditions:
            if b0_u_val == 0:
                qc.x(b0_u)
            if b1_u_val == 0:
                qc.x(b1_u)
            if b0_v_val == 0:
                qc.x(b0_v)
            if b1_v_val == 0:
                qc.x(b1_v)
            
            qc.mcx([b0_u, b1_u, b0_v, b1_v], temp2)
            
            qc.x(same_color)
            qc.ccx(same_color, temp2, same_color)
            qc.x(same_color)
            
            qc.mcx([b0_u, b1_u, b0_v, b1_v], temp2)
            
            if b0_v_val == 0:
                qc.x(b0_v)
            if b1_v_val == 0:
                qc.x(b1_v)
            if b1_u_val == 0:
                qc.x(b1_u)
            if b0_u_val == 0:
                qc.x(b0_u)
        
        qc.ccx(same_color, all_valid, all_valid)
