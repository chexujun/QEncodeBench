from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # problem_qubits[2i], problem_qubits[2i+1] = low, high bits of vertex i
    # Vertex 0: qubits 0,1; Vertex 1: qubits 2,3; Vertex 2: qubits 4,5; Vertex 3: qubits 6,7
    # ancilla_qubits[0:3] = edge violation bits; ancilla_qubits[3] = any violation
    
    v0_b0, v0_b1 = problem_qubits[0], problem_qubits[1]
    v1_b0, v1_b1 = problem_qubits[2], problem_qubits[3]
    v2_b0, v2_b1 = problem_qubits[4], problem_qubits[5]
    v3_b0, v3_b1 = problem_qubits[6], problem_qubits[7]
    
    edge_v0, edge_v1, edge_v2, any_v = ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[2], ancilla_qubits[3]
    
    # Helper: compute same_color(u_b0, u_b1, v_b0, v_b1, out_anc, temps[2])
    # Predicate: (u1 XNOR u0 AND v1 XNOR v0) OR (u0 AND NOT u1 AND v0 AND NOT v1) OR (NOT u0 AND u1 AND NOT v0 AND v1)
    def compute_same_color(u0, u1, v0, v1, out, tmp0, tmp1):
        # Term 1: (u1 XNOR u0 AND v1 XNOR v0)
        # Compute u1 XOR u0 into tmp0
        qc.cx(u0, tmp0)
        qc.cx(u1, tmp0)
        # Compute v1 XOR v0 into tmp1
        qc.cx(v0, tmp1)
        qc.cx(v1, tmp1)
        # Invert tmp0 and tmp1 (now XNOR)
        qc.x(tmp0)
        qc.x(tmp1)
        # Term1 = tmp0 AND tmp1 into out
        qc.ccx(tmp0, tmp1, out)
        # Uncompute tmp0, tmp1
        qc.x(tmp1)
        qc.x(tmp0)
        qc.cx(v1, tmp1)
        qc.cx(v0, tmp1)
        qc.cx(u1, tmp0)
        qc.cx(u0, tmp0)
        
        # Term 2: (u0 AND NOT u1 AND v0 AND NOT v1)
        qc.x(u1)
        qc.x(v1)
        # Compute u0 AND NOT u1 into tmp0
        qc.ccx(u0, u1, tmp0)
        # Compute v0 AND NOT v1 into tmp1
        qc.ccx(v0, v1, tmp1)
        # OR tmp0 into out
        qc.ccx(tmp0, tmp1, any_v)
        qc.cx(any_v, out)
        qc.ccx(tmp0, tmp1, any_v)
        # Uncompute tmp0, tmp1
        qc.ccx(v0, v1, tmp1)
        qc.ccx(u0, u1, tmp0)
        qc.x(v1)
        qc.x(u1)
        
        # Term 3: (NOT u0 AND u1 AND NOT v0 AND v1)
        qc.x(u0)
        qc.x(v0)
        # Compute NOT u0 AND u1 into tmp0
        qc.ccx(u0, u1, tmp0)
        # Compute NOT v0 AND v1 into tmp1
        qc.ccx(v0, v1, tmp1)
        # OR tmp0 into out
        qc.ccx(tmp0, tmp1, any_v)
        qc.cx(any_v, out)
        qc.ccx(tmp0, tmp1, any_v)
        # Uncompute tmp0, tmp1
        qc.ccx(v0, v1, tmp1)
        qc.ccx(u0, u1, tmp0)
        qc.x(v0)
        qc.x(u0)
    
    # Compute edge violations
    compute_same_color(v0_b0, v0_b1, v2_b0, v2_b1, edge_v0, edge_v1, edge_v2)
    compute_same_color(v1_b0, v1_b1, v2_b0, v2_b1, edge_v1, edge_v0, edge_v2)
    compute_same_color(v2_b0, v2_b1, v3_b0, v3_b1, edge_v2, edge_v0, edge_v1)
    
    # Compute any_v = edge_v0 OR edge_v1 OR edge_v2
    qc.cx(edge_v0, any_v)
    qc.cx(edge_v1, any_v)
    qc.cx(edge_v2, any_v)
    
    # Apply phase -1 if NOT any_v (i.e., no edges violated)
    qc.x(any_v)
    qc.z(any_v)
    qc.x(any_v)
    
    # Uncompute any_v
    qc.cx(edge_v2, any_v)
    qc.cx(edge_v1, any_v)
    qc.cx(edge_v0, any_v)
    
    # Uncompute edge violations (reverse order)
    compute_same_color(v2_b0, v2_b1, v3_b0, v3_b1, edge_v2, edge_v0, edge_v1)
    compute_same_color(v1_b0, v1_b1, v2_b0, v2_b1, edge_v1, edge_v0, edge_v2)
    compute_same_color(v0_b0, v0_b1, v2_b0, v2_b1, edge_v0, edge_v1, edge_v2)
