from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0,1), (0,2), (0,3), (0,4), (1,4), (2,3), (3,4)]
    
    def get_color_qubits(v):
        return problem_qubits[2*v], problem_qubits[2*v+1]
    
    def compute_same_color(qc, b0_u, b1_u, b0_v, b1_v, out_ancilla):
        """Compute if two vertices have the same color (color codes map to same color)"""
        patterns = [
            [1, 1, 1, 1],  # (00, 00)
            [1, 1, 0, 0],  # (00, 11)
            [0, 1, 0, 1],  # (01, 01)
            [1, 0, 1, 0],  # (10, 10)
            [0, 0, 1, 1],  # (11, 00)
            [0, 0, 0, 0],  # (11, 11)
        ]
        qubits = [b0_u, b1_u, b0_v, b1_v]
        for neg_pattern in patterns:
            for q, n in zip(qubits, neg_pattern):
                if n:
                    qc.x(q)
            qc.mcx(qubits, out_ancilla)
            for q, n in zip(qubits, neg_pattern):
                if n:
                    qc.x(q)
    
    def cx_swap(qc, a, b):
        """Swap qubits a and b using CX gates"""
        qc.cx(a, b)
        qc.cx(b, a)
        qc.cx(a, b)
    
    qc.x(ancilla_qubits[0])
    
    for u, v in edges:
        b0_u, b1_u = get_color_qubits(u)
        b0_v, b1_v = get_color_qubits(v)
        
        compute_same_color(qc, b0_u, b1_u, b0_v, b1_v, ancilla_qubits[1])
        qc.x(ancilla_qubits[1])
        
        qc.mcx([ancilla_qubits[0], ancilla_qubits[1]], ancilla_qubits[2])
        
        cx_swap(qc, ancilla_qubits[0], ancilla_qubits[2])
        
        qc.x(ancilla_qubits[1])
        compute_same_color(qc, b0_u, b1_u, b0_v, b1_v, ancilla_qubits[1])
    
    qc.z(ancilla_qubits[0])
    
    for u, v in reversed(edges):
        b0_u, b1_u = get_color_qubits(u)
        b0_v, b1_v = get_color_qubits(v)
        
        compute_same_color(qc, b0_u, b1_u, b0_v, b1_v, ancilla_qubits[1])
        qc.x(ancilla_qubits[1])
        
        qc.mcx([ancilla_qubits[0], ancilla_qubits[1]], ancilla_qubits[2])
        
        cx_swap(qc, ancilla_qubits[0], ancilla_qubits[2])
        
        qc.x(ancilla_qubits[1])
        compute_same_color(qc, b0_u, b1_u, b0_v, b1_v, ancilla_qubits[1])
    
    qc.x(ancilla_qubits[0])
