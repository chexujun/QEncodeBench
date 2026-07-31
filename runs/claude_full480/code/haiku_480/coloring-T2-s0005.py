from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    # Edges: (0,1), (0,3), (1,2), (1,3), (3,4)
    edges = [(0, 1), (0, 3), (1, 2), (1, 3), (3, 4)]
    
    # Compute edge constraints into ancilla_qubits[0] to ancilla_qubits[4]
    # For each edge (u, v), the 2-bit codes are (b0_u, b1_u) and (b0_v, b1_v).
    # Colors differ iff (b0_u XOR b0_v) XOR (b1_u XOR b1_v) = 1.
    # This is computed by XORing all four bits into the ancilla.
    for i, (u, v) in enumerate(edges):
        b0_u, b1_u = problem_qubits[2*u], problem_qubits[2*u + 1]
        b0_v, b1_v = problem_qubits[2*v], problem_qubits[2*v + 1]
        
        qc.cx(b0_u, ancilla_qubits[i])
        qc.cx(b0_v, ancilla_qubits[i])
        qc.cx(b1_u, ancilla_qubits[i])
        qc.cx(b1_v, ancilla_qubits[i])
    
    # ancilla_qubits[0:5] now contain the "colors different" flag for each edge
    result_ancilla = ancilla_qubits[5]
    
    # Compute AND of all edge constraints using multi-controlled X
    qc.mcx(ancilla_qubits[0:5], result_ancilla)
    
    # Apply phase -1 to basis states where all edges differ
    qc.z(result_ancilla)
    
    # Uncompute the AND (mcx is self-inverse)
    qc.mcx(ancilla_qubits[0:5], result_ancilla)
    
    # Uncompute edge constraints (mirror of compute phase)
    for i in range(len(edges) - 1, -1, -1):
        u, v = edges[i]
        b0_u, b1_u = problem_qubits[2*u], problem_qubits[2*u + 1]
        b0_v, b1_v = problem_qubits[2*v], problem_qubits[2*v + 1]
        
        qc.cx(b1_v, ancilla_qubits[i])
        qc.cx(b1_u, ancilla_qubits[i])
        qc.cx(b0_v, ancilla_qubits[i])
        qc.cx(b0_u, ancilla_qubits[i])
