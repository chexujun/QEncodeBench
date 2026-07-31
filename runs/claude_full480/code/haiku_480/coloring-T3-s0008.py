from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0,4), (0,5), (1,3), (1,4), (2,3), (2,5), (3,4), (3,5)]
    
    # Initialize accumulator to 1
    qc.x(ancilla_qubits[3])
    
    def process_edge(u, v):
        """Compute whether edge (u,v) is valid and AND with accumulator."""
        u0, u1 = problem_qubits[2*u], problem_qubits[2*u+1]
        v0, v1 = problem_qubits[2*v], problem_qubits[2*v+1]
        a = ancilla_qubits
        
        # Compute parity_u = u0 XOR u1
        qc.cx(u0, a[0])
        qc.cx(u1, a[0])
        
        # Compute parity_v = v0 XOR v1
        qc.cx(v0, a[1])
        qc.cx(v1, a[1])
        
        # Compute u0 XOR v0
        qc.cx(u0, a[2])
        qc.cx(v0, a[2])
        
        # edge_valid = (parity_u XOR parity_v) OR ((parity_u AND parity_v) AND (u0 XOR v0))
        
        # First term: parity_u XOR parity_v
        qc.cx(a[0], a[4])
        qc.cx(a[1], a[4])
        
        # Second term: compute parity_u AND parity_v
        qc.ccx(a[0], a[1], a[0])  # a[0] now has parity_u AND parity_v
        
        # Then AND with (u0 XOR v0)
        qc.ccx(a[0], a[2], a[1])  # a[1] now has the full second term
        
        # Compute OR of a[4] and a[1]: result in a[0]
        qc.ccx(a[4], a[1], a[0])  # AND for the OR formula
        qc.cx(a[4], a[0])
        qc.cx(a[1], a[0])
        # a[0] now contains edge_valid
        
        # AND with accumulator: accumulator = accumulator AND edge_valid
        qc.ccx(a[0], a[3], a[2])
        qc.cx(a[3], a[0])
        qc.cx(a[2], a[3])
        qc.cx(a[0], a[2])
        
        # Uncompute in reverse order
        qc.cx(a[1], a[0])
        qc.cx(a[4], a[0])
        qc.ccx(a[4], a[1], a[0])
        
        qc.ccx(a[0], a[2], a[1])
        qc.cx(u0, a[0])
        qc.cx(u1, a[0])
        qc.cx(v0, a[1])
        qc.cx(v1, a[1])
        qc.ccx(a[0], a[1], a[0])
        
        qc.cx(a[1], a[4])
        qc.cx(a[0], a[4])
        
        qc.cx(v0, a[2])
        qc.cx(u0, a[2])
        
        qc.cx(v1, a[1])
        qc.cx(v0, a[1])
        
        qc.cx(u1, a[0])
        qc.cx(u0, a[0])
    
    # Forward pass
    for u, v in edges:
        process_edge(u, v)
    
    # Apply phase
    qc.z(ancilla_qubits[3])
    
    # Reverse pass
    for u, v in reversed(edges):
        process_edge(u, v)
