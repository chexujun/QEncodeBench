from qiskit import QuantumCircuit

def build_oracle(qc, problem_qubits, ancilla_qubits):
    edges = [(0, 1), (0, 2), (0, 4), (1, 5), (2, 3), (2, 4), (2, 5), (3, 5)]
    
    valid = ancilla_qubits[0]
    qc.x(valid)
    
    for u, v in edges:
        u_b0, u_b1 = problem_qubits[2*u], problem_qubits[2*u+1]
        v_b0, v_b1 = problem_qubits[2*v], problem_qubits[2*v+1]
        
        mono = ancilla_qubits[1]
        tmp = [ancilla_qubits[i+2] for i in range(3)]
        
        # Condition 1: both color 0
        qc.cx(u_b0, tmp[0])
        qc.cx(u_b1, tmp[0])
        qc.cx(v_b0, tmp[1])
        qc.cx(v_b1, tmp[1])
        qc.x(tmp[0])
        qc.x(tmp[1])
        qc.ccx(tmp[0], tmp[1], mono)
        qc.x(tmp[0])
        qc.x(tmp[1])
        qc.cx(u_b0, tmp[0])
        qc.cx(u_b1, tmp[0])
        qc.cx(v_b0, tmp[1])
        qc.cx(v_b1, tmp[1])
        
        # Condition 2: both color 1
        qc.x(u_b1)
        qc.ccx(u_b0, u_b1, tmp[0])
        qc.x(u_b1)
        qc.x(v_b1)
        qc.ccx(v_b0, v_b1, tmp[1])
        qc.x(v_b1)
        qc.ccx(tmp[0], tmp[1], tmp[2])
        qc.cx(tmp[2], mono)
        qc.ccx(tmp[0], tmp[1], tmp[2])
        qc.x(u_b1)
        qc.ccx(u_b0, u_b1, tmp[0])
        qc.x(u_b1)
        qc.x(v_b1)
        qc.ccx(v_b0, v_b1, tmp[1])
        qc.x(v_b1)
        
        # Condition 3: both color 2
        qc.x(u_b0)
        qc.ccx(u_b0, u_b1, tmp[0])
        qc.x(u_b0)
        qc.x(v_b0)
        qc.ccx(v_b0, v_b1, tmp[1])
        qc.x(v_b0)
        qc.ccx(tmp[0], tmp[1], tmp[2])
        qc.cx(tmp[2], mono)
        qc.ccx(tmp[0], tmp[1], tmp[2])
        qc.x(u_b0)
        qc.ccx(u_b0, u_b1, tmp[0])
        qc.x(u_b0)
        qc.x(v_b0)
        qc.ccx(v_b0, v_b1, tmp[1])
        qc.x(v_b0)
        
        # Update validity
        qc.ccx(valid, mono, valid)
        
        # Uncompute condition 3
        qc.x(u_b0)
        qc.ccx(u_b0, u_b1, tmp[0])
        qc.x(u_b0)
        qc.x(v_b0)
        qc.ccx(v_b0, v_b1, tmp[1])
        qc.x(v_b0)
        qc.ccx(tmp[0], tmp[1], tmp[2])
        qc.cx(tmp[2], mono)
        qc.ccx(tmp[0], tmp[1], tmp[2])
        qc.x(u_b0)
        qc.ccx(u_b0, u_b1, tmp[0])
        qc.x(u_b0)
        qc.x(v_b0)
        qc.ccx(v_b0, v_b1, tmp[1])
        qc.x(v_b0)
        
        # Uncompute condition 2
        qc.x(u_b1)
        qc.ccx(u_b0, u_b1, tmp[0])
        qc.x(u_b1)
        qc.x(v_b1)
        qc.ccx(v_b0, v_b1, tmp[1])
        qc.x(v_b1)
        qc.ccx(tmp[0], tmp[1], tmp[2])
        qc.cx(tmp[2], mono)
        qc.ccx(tmp[0], tmp[1], tmp[2])
        qc.x(u_b1)
        qc.ccx(u_b0, u_b1, tmp[0])
        qc.x(u_b1)
        qc.x(v_b1)
        qc.ccx(v_b0, v_b1, tmp[1])
        qc.x(v_b1)
        
        # Uncompute condition 1
        qc.cx(u_b0, tmp[0])
        qc.cx(u_b1, tmp[0])
        qc.cx(v_b0, tmp[1])
        qc.cx(v_b1, tmp[1])
        qc.x(tmp[0])
        qc.x(tmp[1])
        qc.ccx(tmp[0], tmp[1], mono)
        qc.x(tmp[0])
        qc.x(tmp[1])
        qc.cx(u_b0, tmp[0])
        qc.cx(u_b1, tmp[0])
        qc.cx(v_b0, tmp[1])
        qc.cx(v_b1, tmp[1])
    
    qc.z(valid)
    qc.x(valid)
