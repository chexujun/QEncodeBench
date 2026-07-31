from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0,1), (0,4), (1,2), (1,3), (1,4), (2,4), (3,4)]
    
    violation = ancilla_qubits[3]
    
    for u, v in edges:
        b0_u, b1_u = problem_qubits[2*u], problem_qubits[2*u+1]
        b0_v, b1_v = problem_qubits[2*v], problem_qubits[2*v+1]
        
        t0, t1, t2 = ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[2]
        
        # Compute XOR of bits for each pair
        qc.cx(b0_u, t0)
        qc.cx(b0_v, t0)
        qc.cx(b1_u, t1)
        qc.cx(b1_v, t1)
        
        # Check condition 1: codes are identical (b0_u==b0_v AND b1_u==b1_v)
        qc.x(t0)
        qc.x(t1)
        qc.ccx(t0, t1, t2)
        qc.cx(t2, violation)
        qc.ccx(t0, t1, t2)
        qc.x(t0)
        qc.x(t1)
        
        # Uncompute XOR
        qc.cx(b0_u, t0)
        qc.cx(b0_v, t0)
        qc.cx(b1_u, t1)
        qc.cx(b1_v, t1)
        
        # Check condition 2: b0_u==b1_u AND (b0_u XOR b0_v) AND (b1_u XOR b1_v)
        qc.cx(b0_u, t0)
        qc.cx(b1_u, t0)
        qc.cx(b0_u, t1)
        qc.cx(b0_v, t1)
        qc.cx(b1_u, t2)
        qc.cx(b1_v, t2)
        
        qc.x(t0)
        qc.ccx(t0, t1, violation)
        qc.ccx(violation, t2, violation)
        qc.ccx(t0, t1, violation)
        qc.x(t0)
        
        qc.cx(b0_u, t0)
        qc.cx(b1_u, t0)
        qc.cx(b0_u, t1)
        qc.cx(b0_v, t1)
        qc.cx(b1_u, t2)
        qc.cx(b1_v, t2)
    
    qc.x(violation)
    qc.z(violation)
    qc.x(violation)
