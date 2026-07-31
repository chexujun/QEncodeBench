from qiskit import QuantumCircuit

def build_oracle(qc, problem_qubits, ancilla_qubits):
    edges = [(0, 1), (0, 2), (0, 3), (0, 4), (1, 2), (2, 3), (2, 4)]
    
    # Ancilla allocation:
    # 0-6: store monochromatic flag for each edge
    # 7: temporary for XOR and AND computations
    
    # COMPUTE STAGE: Compute all edge monochromatic flags
    for edge_idx, (u, v) in enumerate(edges):
        u_b0, u_b1 = problem_qubits[2*u], problem_qubits[2*u + 1]
        v_b0, v_b1 = problem_qubits[2*v], problem_qubits[2*v + 1]
        
        mono_anc = ancilla_qubits[edge_idx]
        temp = ancilla_qubits[7]
        
        # Compute monochromatic = (b1_u XNOR b1_v) AND (b0_u XNOR b0_v)
        # = (NOT(b1_u XOR b1_v)) AND (NOT(b0_u XOR b0_v))
        
        # Compute b1_u XOR b1_v into temp
        qc.cx(u_b1, temp)
        qc.cx(v_b1, temp)
        
        # Compute b0_u XOR b0_v into mono_anc (we'll use it for AND)
        qc.cx(u_b0, mono_anc)
        qc.cx(v_b0, mono_anc)
        
        # Now compute AND of (NOT temp) and (NOT mono_anc)
        qc.x(temp)
        qc.x(mono_anc)
        qc.mcx([temp, mono_anc], ancilla_qubits[6])  # Use ancilla 6 as AND result temporarily
        qc.x(mono_anc)
        qc.x(temp)
        
        # Move AND result back to mono_anc
        qc.cx(ancilla_qubits[6], mono_anc)
        
        # Uncompute temp and ancilla_qubits[6]
        qc.cx(v_b1, temp)
        qc.cx(u_b1, temp)
        
        qc.x(mono_anc)
        qc.x(temp)
        qc.mcx([temp, mono_anc], ancilla_qubits[6])
        qc.x(temp)
        qc.x(mono_anc)
        
        qc.cx(v_b0, mono_anc)
        qc.cx(u_b0, mono_anc)
    
    # PHASE STAGE: Apply phase -1 if no edge is monochromatic (all valid)
    # valid = NOT(mono_0 OR mono_1 OR ... OR mono_6)
    # Use iterative OR reduction
    result = ancilla_qubits[7]
    
    # OR all mono flags together into result
    for idx in range(7):
        mono_i = ancilla_qubits[idx]
        # result = result OR mono_i using temporary ancilla_qubits[6]
        qc.x(result)
        qc.x(mono_i)
        qc.mcx([result, mono_i], ancilla_qubits[6])
        qc.x(ancilla_qubits[6])
        qc.cx(ancilla_qubits[6], result)
        qc.x(ancilla_qubits[6])
        qc.x(mono_i)
        qc.x(result)
    
    # Apply Z if result = 0 (no edges monochromatic = all valid)
    qc.x(result)
    qc.z(result)
    qc.x(result)
    
    # UNCOMPUTE STAGE: Reverse the OR reductions and clear ancillas
    for idx in range(6, -1, -1):
        mono_i = ancilla_qubits[idx]
        qc.x(result)
        qc.x(mono_i)
        qc.mcx([result, mono_i], ancilla_qubits[6])
        qc.x(ancilla_qubits[6])
        qc.cx(ancilla_qubits[6], result)
        qc.x(ancilla_qubits[6])
        qc.x(mono_i)
        qc.x(result)
    
    # Uncompute edge monochromatic values (reverse of compute stage)
    for edge_idx in range(6, -1, -1):
        u, v = edges[edge_idx]
        u_b0, u_b1 = problem_qubits[2*u], problem_qubits[2*u + 1]
        v_b0, v_b1 = problem_qubits[2*v], problem_qubits[2*v + 1]
        
        mono_anc = ancilla_qubits[edge_idx]
        temp = ancilla_qubits[7]
        
        qc.cx(v_b0, mono_anc)
        qc.cx(u_b0, mono_anc)
        
        qc.x(mono_anc)
        qc.x(temp)
        qc.mcx([temp, mono_anc], ancilla_qubits[6])
        qc.x(temp)
        qc.x(mono_anc)
        
        qc.cx(ancilla_qubits[6], mono_anc)
        
        qc.cx(v_b1, temp)
        qc.cx(u_b1, temp)
        
        qc.x(temp)
        qc.x(mono_anc)
        qc.mcx([temp, mono_anc], ancilla_qubits[6])
        qc.x(mono_anc)
        qc.x(temp)
        
        qc.cx(v_b0, mono_anc)
        qc.cx(u_b0, mono_anc)
