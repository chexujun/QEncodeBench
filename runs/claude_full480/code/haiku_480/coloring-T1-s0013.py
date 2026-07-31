from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 1), (0, 3), (1, 2)]
    
    def get_vertex_qubits(v):
        return problem_qubits[2*v], problem_qubits[2*v+1]
    
    flag = ancilla_qubits[0]
    qc.x(flag)
    
    for u, v in edges:
        low_u, high_u = get_vertex_qubits(u)
        low_v, high_v = get_vertex_qubits(v)
        
        qc.x(low_u)
        qc.x(high_u)
        qc.x(low_v)
        qc.x(high_v)
        qc.mcx([low_u, high_u, low_v, high_v], flag)
        qc.x(low_u)
        qc.x(high_u)
        qc.x(low_v)
        qc.x(high_v)
        
        qc.x(low_u)
        qc.x(high_u)
        qc.mcx([low_u, high_u, low_v, high_v], flag)
        qc.x(low_u)
        qc.x(high_u)
        
        qc.x(low_v)
        qc.x(high_v)
        qc.mcx([low_u, high_u, low_v, high_v], flag)
        qc.x(low_v)
        qc.x(high_v)
        
        qc.mcx([low_u, high_u, low_v, high_v], flag)
        
        qc.x(high_u)
        qc.x(high_v)
        qc.mcx([low_u, high_u, low_v, high_v], flag)
        qc.x(high_u)
        qc.x(high_v)
        
        qc.x(low_u)
        qc.x(low_v)
        qc.mcx([low_u, high_u, low_v, high_v], flag)
        qc.x(low_u)
        qc.x(low_v)
    
    qc.cz(flag, problem_qubits[0])
    
    for u, v in reversed(edges):
        low_u, high_u = get_vertex_qubits(u)
        low_v, high_v = get_vertex_qubits(v)
        
        qc.x(low_u)
        qc.x(low_v)
        qc.mcx([low_u, high_u, low_v, high_v], flag)
        qc.x(low_u)
        qc.x(low_v)
        
        qc.x(high_u)
        qc.x(high_v)
        qc.mcx([low_u, high_u, low_v, high_v], flag)
        qc.x(high_u)
        qc.x(high_v)
        
        qc.mcx([low_u, high_u, low_v, high_v], flag)
        
        qc.x(low_v)
        qc.x(high_v)
        qc.mcx([low_u, high_u, low_v, high_v], flag)
        qc.x(low_v)
        qc.x(high_v)
        
        qc.x(low_u)
        qc.x(high_u)
        qc.mcx([low_u, high_u, low_v, high_v], flag)
        qc.x(low_u)
        qc.x(high_u)
        
        qc.x(low_u)
        qc.x(high_u)
        qc.x(low_v)
        qc.x(high_v)
        qc.mcx([low_u, high_u, low_v, high_v], flag)
        qc.x(low_u)
        qc.x(high_u)
        qc.x(low_v)
        qc.x(high_v)
    
    qc.x(flag)
