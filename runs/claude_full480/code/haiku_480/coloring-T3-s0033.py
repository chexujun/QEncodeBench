from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0,1), (0,2), (0,4), (1,3), (2,3), (2,4), (3,4)]
    
    violation_flag = ancilla_qubits[0]
    
    for u, v in edges:
        u0, u1 = problem_qubits[2*u], problem_qubits[2*u+1]
        v0, v1 = problem_qubits[2*v], problem_qubits[2*v+1]
        
        # Same color happens when:
        # (NOT(u0 XOR v0) AND NOT(u1 XOR v1)) OR
        # (NOT u0 AND NOT u1 AND v0 AND v1) OR
        # (u0 AND u1 AND NOT v0 AND NOT v1)
        
        w0, w1, w2 = ancilla_qubits[1], ancilla_qubits[2], ancilla_qubits[3]
        
        # Term 1
        qc.cx(u0, w0)
        qc.cx(v0, w0)
        qc.cx(u1, w1)
        qc.cx(v1, w1)
        qc.x(w0)
        qc.x(w1)
        qc.ccx(w0, w1, w2)
        qc.x(w0)
        qc.x(w1)
        qc.cx(v0, w0)
        qc.cx(u0, w0)
        qc.cx(v1, w1)
        qc.cx(u1, w1)
        
        # Term 2: (NOT u0 AND NOT u1 AND v0 AND v1)
        qc.x(u0)
        qc.x(u1)
        qc.mcx([u0, u1, v0, v1], w0)
        qc.x(u0)
        qc.x(u1)
        
        # OR: w2 OR w0 -> w1
        qc.x(w2)
        qc.x(w0)
        qc.ccx(w2, w0, w1)
        qc.x(w2)
        qc.x(w0)
        qc.x(w1)
        
        # Term 3: (u0 AND u1 AND NOT v0 AND NOT v1)
        qc.x(v0)
        qc.x(v1)
        qc.mcx([u0, u1, v0, v1], w2)
        qc.x(v0)
        qc.x(v1)
        
        # OR: w1 OR w2 -> w0
        qc.x(w1)
        qc.x(w2)
        qc.ccx(w1, w2, w0)
        qc.x(w1)
        qc.x(w2)
        qc.x(w0)
        
        # w0 = same_color. OR into violation_flag
        qc.x(w0)
        qc.x(violation_flag)
        qc.ccx(w0, violation_flag, w1)
        qc.x(w0)
        qc.x(violation_flag)
        qc.x(w1)
        qc.cx(w1, violation_flag)
    
    # Phase gate: -1 when violation_flag = 0 (no violations)
    qc.x(violation_flag)
    qc.z(violation_flag)
    qc.x(violation_flag)
