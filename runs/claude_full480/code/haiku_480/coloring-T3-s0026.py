from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    result = ancilla_qubits[0]
    temp = ancilla_qubits[1]
    
    edges = [(0,1), (0,4), (0,5), (1,3), (1,4), (2,3), (2,4), (3,5)]
    
    # Forward pass: compute XOR of same_color for all edges
    for u, v in edges:
        u0, u1 = problem_qubits[2*u], problem_qubits[2*u+1]
        v0, v1 = problem_qubits[2*v], problem_qubits[2*v+1]
        
        compute_same_color(qc, u0, u1, v0, v1, temp)
        qc.cx(temp, result)
        uncompute_same_color(qc, u0, u1, v0, v1, temp)
    
    # Apply phase -1 when result = 0 (valid coloring)
    qc.x(result)
    qc.z(result)
    qc.x(result)
    
    # Backward pass: uncompute to restore result to 0
    for u, v in reversed(edges):
        u0, u1 = problem_qubits[2*u], problem_qubits[2*u+1]
        v0, v1 = problem_qubits[2*v], problem_qubits[2*v+1]
        
        compute_same_color(qc, u0, u1, v0, v1, temp)
        qc.cx(temp, result)
        uncompute_same_color(qc, u0, u1, v0, v1, temp)


def compute_same_color(qc, u0, u1, v0, v1, temp):
    """Compute same_color predicate into temp qubit using minterm enumeration."""
    minterms = [0, 3, 5, 10, 12, 15]
    qubits = [u0, u1, v0, v1]
    
    for minterm in minterms:
        # Flip qubits to match minterm pattern
        for i, qubit in enumerate(qubits):
            if not (minterm & (1 << i)):
                qc.x(qubit)
        
        # Apply 4-qubit AND
        qc.mcx(qubits, temp)
        
        # Flip back
        for i, qubit in enumerate(qubits):
            if not (minterm & (1 << i)):
                qc.x(qubit)


def uncompute_same_color(qc, u0, u1, v0, v1, temp):
    """Uncompute same_color, restoring temp to 0."""
    minterms = [15, 12, 10, 5, 3, 0]
    qubits = [u0, u1, v0, v1]
    
    for minterm in minterms:
        # Flip qubits to match minterm pattern
        for i, qubit in enumerate(qubits):
            if not (minterm & (1 << i)):
                qc.x(qubit)
        
        # Apply 4-qubit AND
        qc.mcx(qubits, temp)
        
        # Flip back
        for i, qubit in enumerate(qubits):
            if not (minterm & (1 << i)):
                qc.x(qubit)
