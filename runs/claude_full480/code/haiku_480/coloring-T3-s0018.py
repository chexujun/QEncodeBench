from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0,1), (0,3), (0,4), (1,2), (1,3), (2,3), (3,4)]
    
    # Use ancilla_qubits[0] as the accumulator (f(x) result)
    f_result = ancilla_qubits[0]
    qc.x(f_result)  # Initialize to 1 (meaning "all constraints satisfied")
    
    # Process each edge
    for u, v in edges:
        u0, u1 = problem_qubits[2*u], problem_qubits[2*u+1]
        v0, v1 = problem_qubits[2*v], problem_qubits[2*v+1]
        
        # Compute whether u and v have the same color into ancilla_qubits[1]
        same_color = ancilla_qubits[1]
        w1 = ancilla_qubits[2]
        w2 = ancilla_qubits[3]
        
        # same_color is true iff (u_code % 3) == (v_code % 3)
        # This happens for: (00,00), (00,11), (11,00), (11,11), (01,01), (10,10)
        # Condition 1: (u1 XNOR u0) AND (v1 XNOR v0)  [covers 00,00 and 11,11 pairs]
        # Condition 2: (NOT u1 AND u0) AND (NOT v1 AND v0)  [covers 01,01]
        # Condition 3: (u1 AND NOT u0) AND (v1 AND NOT v0)  [covers 10,10]
        
        # Compute u1 XNOR u0 into w1
        qc.cx(u1, w1)
        qc.cx(u0, w1)
        qc.x(w1)  # w1 = u1 XNOR u0
        
        # Compute v1 XNOR v0 into w2
        qc.cx(v1, w2)
        qc.cx(v0, w2)
        qc.x(w2)  # w2 = v1 XNOR v0
        
        # Condition 1: w1 AND w2
        qc.ccx(w1, w2, same_color)  # same_color = Cond1
        
        # Uncompute w1, w2
        qc.x(w2)
        qc.cx(v0, w2)
        qc.cx(v1, w2)
        qc.x(w1)
        qc.cx(u0, w1)
        qc.cx(u1, w1)
        
        # Compute Condition 2: (NOT u1 AND u0) AND (NOT v1 AND v0)
        qc.x(u1)
        qc.ccx(u1, u0, w1)
        qc.x(u1)  # w1 = NOT u1 AND u0
        
        qc.x(v1)
        qc.ccx(v1, v0, w2)
        qc.x(v1)  # w2 = NOT v1 AND v0
        
        # OR Condition 2 into same_color using: a OR b = NOT(NOT a AND NOT b)
        qc.x(same_color)
        qc.x(w1)
        qc.ccx(same_color, w1, w2)  # w2 used as temporary to hold NOT same_color AND NOT w1
        qc.x(w1)
        qc.x(same_color)
        qc.x(w2)  # w2 = NOT(NOT same_color AND NOT w1) = same_color OR w1
        qc.cx(w2, same_color)
        qc.x(w2)
        
        # Uncompute w1
        qc.x(u1)
        qc.ccx(u1, u0, w1)
        qc.x(u1)
        
        # Compute Condition 3: (u1 AND NOT u0) AND (v1 AND NOT v0)
        qc.x(u0)
        qc.ccx(u1, u0, w1)
        qc.x(u0)  # w1 = u1 AND NOT u0
        
        qc.x(v0)
        qc.ccx(v1, v0, w2)
        qc.x(v0)  # w2 = v1 AND NOT v0
        
        # OR Condition 3 into same_color
        qc.x(same_color)
        qc.x(w1)
        qc.ccx(same_color, w1, w2)
        qc.x(w1)
        qc.x(same_color)
        qc.x(w2)
        qc.cx(w2, same_color)
        qc.x(w2)
        
        # Uncompute w1
        qc.x(u0)
        qc.ccx(u1, u0, w1)
        qc.x(u0)
        
        # Update f_result: f_result = f_result AND NOT same_color
        qc.ccx(same_color, f_result, f_result)
        
        # Uncompute same_color (mirror the computation)
        # Uncompute Condition 3
        qc.x(v0)
        qc.ccx(v1, v0, w2)
        qc.x(v0)
        qc.x(u0)
        qc.ccx(u1, u0, w1)
        qc.x(u0)
        
        # Uncompute OR
        qc.x(w2)
        qc.cx(w2, same_color)
        qc.x(w2)
        qc.x(same_color)
        qc.x(w1)
        qc.ccx(same_color, w1, w2)
        qc.x(w1)
        qc.x(same_color)
        
        # Uncompute Condition 2
        qc.x(v1)
        qc.ccx(v1, v0, w2)
        qc.x(v1)
        qc.x(u1)
        qc.ccx(u1, u0, w1)
        qc.x(u1)
        
        # Uncompute OR
        qc.x(w2)
        qc.cx(w2, same_color)
        qc.x(w2)
        qc.x(same_color)
        qc.x(w1)
        qc.ccx(same_color, w1, w2)
        qc.x(w1)
        qc.x(same_color)
        
        # Uncompute Condition 1
        qc.x(w2)
        qc.cx(v0, w2)
        qc.cx(v1, w2)
        qc.x(w1)
        qc.cx(u0, w1)
        qc.cx(u1, w1)
        qc.ccx(w1, w2, same_color)
    
    # Apply phase
    qc.z(f_result)
    
    # Uncompute f_result initialization
    qc.x(f_result)
