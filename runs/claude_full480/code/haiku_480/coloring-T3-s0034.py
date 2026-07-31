from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0,1), (0,2), (1,4), (1,5), (2,3), (3,4), (4,5)]
    
    valid = ancilla_qubits[0]
    same_color = ancilla_qubits[1]
    temp1 = ancilla_qubits[2]
    temp2 = ancilla_qubits[3]
    
    qc.x(valid)
    
    for u, v in edges:
        u0, u1 = problem_qubits[2*u], problem_qubits[2*u+1]
        v0, v1 = problem_qubits[2*v], problem_qubits[2*v+1]
        
        # Compute: same_color = (u0==v0 AND u1==v1) OR complementary color-0 codes
        
        # Case 1: Identical codes (u0 XNOR v0) AND (u1 XNOR v1)
        qc.cx(u0, temp1)
        qc.cx(v0, temp1)
        qc.x(temp1)
        
        qc.cx(u1, temp2)
        qc.cx(v1, temp2)
        qc.x(temp2)
        
        qc.ccx(temp1, temp2, same_color)
        
        qc.x(temp2)
        qc.cx(v1, temp2)
        qc.cx(u1, temp2)
        
        qc.x(temp1)
        qc.cx(v0, temp1)
        qc.cx(u0, temp1)
        
        # Case 2: (u0, u1, v0, v1) = (0, 0, 1, 1)
        qc.x(u0)
        qc.x(u1)
        qc.mcx([u0, u1, v0, v1], same_color)
        qc.x(u1)
        qc.x(u0)
        
        # Case 3: (u0, u1, v0, v1) = (1, 1, 0, 0)
        qc.x(v0)
        qc.x(v1)
        qc.mcx([u0, u1, v0, v1], same_color)
        qc.x(v1)
        qc.x(v0)
        
        # Update valid: valid AND NOT same_color
        qc.ccx(same_color, valid, valid)
        
        # Uncompute same_color in reverse
        qc.x(v0)
        qc.x(v1)
        qc.mcx([u0, u1, v0, v1], same_color)
        qc.x(v1)
        qc.x(v0)
        
        qc.x(u0)
        qc.x(u1)
        qc.mcx([u0, u1, v0, v1], same_color)
        qc.x(u1)
        qc.x(u0)
        
        qc.cx(u0, temp1)
        qc.cx(v0, temp1)
        qc.x(temp1)
        
        qc.cx(u1, temp2)
        qc.cx(v1, temp2)
        qc.x(temp2)
        
        qc.ccx(temp1, temp2, same_color)
        
        qc.x(temp2)
        qc.cx(v1, temp2)
        qc.cx(u1, temp2)
        
        qc.x(temp1)
        qc.cx(v0, temp1)
        qc.cx(u0, temp1)
    
    qc.z(valid)
    
    for u, v in reversed(edges):
        u0, u1 = problem_qubits[2*u], problem_qubits[2*u+1]
        v0, v1 = problem_qubits[2*v], problem_qubits[2*v+1]
        
        qc.cx(u0, temp1)
        qc.cx(v0, temp1)
        qc.x(temp1)
        
        qc.cx(u1, temp2)
        qc.cx(v1, temp2)
        qc.x(temp2)
        
        qc.ccx(temp1, temp2, same_color)
        
        qc.x(temp2)
        qc.cx(v1, temp2)
        qc.cx(u1, temp2)
        
        qc.x(temp1)
        qc.cx(v0, temp1)
        qc.cx(u0, temp1)
        
        qc.x(u0)
        qc.x(u1)
        qc.mcx([u0, u1, v0, v1], same_color)
        qc.x(u1)
        qc.x(u0)
        
        qc.x(v0)
        qc.x(v1)
        qc.mcx([u0, u1, v0, v1], same_color)
        qc.x(v1)
        qc.x(v0)
        
        qc.ccx(same_color, valid, valid)
        
        qc.x(v0)
        qc.x(v1)
        qc.mcx([u0, u1, v0, v1], same_color)
        qc.x(v1)
        qc.x(v0)
        
        qc.x(u0)
        qc.x(u1)
        qc.mcx([u0, u1, v0, v1], same_color)
        qc.x(u1)
        qc.x(u0)
        
        qc.cx(u0, temp1)
        qc.cx(v0, temp1)
        qc.x(temp1)
        
        qc.cx(u1, temp2)
        qc.cx(v1, temp2)
        qc.x(temp2)
        
        qc.ccx(temp1, temp2, same_color)
        
        qc.x(temp2)
        qc.cx(v1, temp2)
        qc.cx(u1, temp2)
        
        qc.x(temp1)
        qc.cx(v0, temp1)
        qc.cx(u0, temp1)
    
    qc.x(valid)
