from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0,1), (0,3), (0,4), (1,2), (1,3), (1,4), (2,4)]
    
    violation = ancilla_qubits[0]
    temp = ancilla_qubits[1]
    
    for u, v in edges:
        u_b0 = problem_qubits[2*u]
        u_b1 = problem_qubits[2*u + 1]
        v_b0 = problem_qubits[2*v]
        v_b1 = problem_qubits[2*v + 1]
        
        # Check condition 1: u==0 AND v==0
        qc.x(u_b0)
        qc.x(u_b1)
        qc.x(v_b0)
        qc.x(v_b1)
        qc.mcx([u_b0, u_b1, v_b0, v_b1], temp)
        qc.x(violation)
        qc.ccx(violation, temp, violation)
        qc.x(violation)
        qc.mcx([u_b0, u_b1, v_b0, v_b1], temp)
        qc.x(v_b1)
        qc.x(v_b0)
        qc.x(u_b1)
        qc.x(u_b0)
        
        # Check condition 2: u==0 AND v==3
        qc.x(u_b0)
        qc.x(u_b1)
        qc.mcx([u_b0, u_b1, v_b0, v_b1], temp)
        qc.x(violation)
        qc.ccx(violation, temp, violation)
        qc.x(violation)
        qc.mcx([u_b0, u_b1, v_b0, v_b1], temp)
        qc.x(u_b1)
        qc.x(u_b0)
        
        # Check condition 3: u==1 AND v==1
        qc.x(u_b1)
        qc.x(v_b1)
        qc.mcx([u_b0, u_b1, v_b0, v_b1], temp)
        qc.x(violation)
        qc.ccx(violation, temp, violation)
        qc.x(violation)
        qc.mcx([u_b0, u_b1, v_b0, v_b1], temp)
        qc.x(v_b1)
        qc.x(u_b1)
        
        # Check condition 4: u==2 AND v==2
        qc.x(u_b0)
        qc.x(v_b0)
        qc.mcx([u_b0, u_b1, v_b0, v_b1], temp)
        qc.x(violation)
        qc.ccx(violation, temp, violation)
        qc.x(violation)
        qc.mcx([u_b0, u_b1, v_b0, v_b1], temp)
        qc.x(v_b0)
        qc.x(u_b0)
        
        # Check condition 5: u==3 AND v==0
        qc.x(v_b0)
        qc.x(v_b1)
        qc.mcx([u_b0, u_b1, v_b0, v_b1], temp)
        qc.x(violation)
        qc.ccx(violation, temp, violation)
        qc.x(violation)
        qc.mcx([u_b0, u_b1, v_b0, v_b1], temp)
        qc.x(v_b1)
        qc.x(v_b0)
        
        # Check condition 6: u==3 AND v==3
        qc.mcx([u_b0, u_b1, v_b0, v_b1], temp)
        qc.x(violation)
        qc.ccx(violation, temp, violation)
        qc.x(violation)
        qc.mcx([u_b0, u_b1, v_b0, v_b1], temp)
    
    # Apply phase -1 iff violation == 0 (no edges violated)
    qc.x(violation)
    qc.z(violation)
    qc.x(violation)
