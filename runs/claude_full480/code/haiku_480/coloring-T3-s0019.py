from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0,1), (0,2), (0,4), (1,3), (1,4), (2,3), (2,4), (3,4)]
    
    all_valid = ancilla_qubits[0]
    temp_xor1 = ancilla_qubits[1]
    temp_xor2 = ancilla_qubits[2]
    edge_valid = ancilla_qubits[3]
    
    qc.x(all_valid)
    
    for u, v in edges:
        b0_u = problem_qubits[2*u]
        b1_u = problem_qubits[2*u+1]
        b0_v = problem_qubits[2*v]
        b1_v = problem_qubits[2*v+1]
        
        qc.cx(b0_u, temp_xor1)
        qc.cx(b0_v, temp_xor1)
        
        qc.cx(b1_u, temp_xor2)
        qc.cx(b1_v, temp_xor2)
        
        qc.cx(temp_xor1, edge_valid)
        qc.cx(temp_xor2, edge_valid)
        
        qc.x(edge_valid)
        qc.cx(edge_valid, all_valid)
        qc.x(edge_valid)
    
    qc.z(all_valid)
    
    for u, v in reversed(edges):
        b0_u = problem_qubits[2*u]
        b1_u = problem_qubits[2*u+1]
        b0_v = problem_qubits[2*v]
        b1_v = problem_qubits[2*v+1]
        
        qc.x(edge_valid)
        qc.cx(edge_valid, all_valid)
        qc.x(edge_valid)
        
        qc.cx(temp_xor2, edge_valid)
        qc.cx(temp_xor1, edge_valid)
        
        qc.cx(b1_v, temp_xor2)
        qc.cx(b1_u, temp_xor2)
        
        qc.cx(b0_v, temp_xor1)
        qc.cx(b0_u, temp_xor1)
    
    qc.x(all_valid)
