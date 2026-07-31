from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 1), (0, 2), (1, 3), (2, 3)]
    
    # Compute whether each edge constraint is satisfied (different colors)
    for edge_idx, (u, v) in enumerate(edges):
        bu0 = problem_qubits[2*u]
        bu1 = problem_qubits[2*u+1]
        bv0 = problem_qubits[2*v]
        bv1 = problem_qubits[2*v+1]
        ancilla = ancilla_qubits[edge_idx]
        
        qc.cx(bu0, ancilla)
        qc.cx(bv0, ancilla)
        qc.cx(bu1, ancilla)
        qc.cx(bv1, ancilla)
    
    # Compute AND of all constraints into ancilla[4]
    qc.mcx([ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[2], ancilla_qubits[3]], ancilla_qubits[4])
    
    # Apply phase: Z gate marks the solution with -1
    qc.z(ancilla_qubits[4])
    
    # Uncompute AND
    qc.mcx([ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[2], ancilla_qubits[3]], ancilla_qubits[4])
    
    # Uncompute constraints
    for edge_idx, (u, v) in enumerate(edges):
        bu0 = problem_qubits[2*u]
        bu1 = problem_qubits[2*u+1]
        bv0 = problem_qubits[2*v]
        bv1 = problem_qubits[2*v+1]
        ancilla = ancilla_qubits[edge_idx]
        
        qc.cx(bv1, ancilla)
        qc.cx(bu1, ancilla)
        qc.cx(bv0, ancilla)
        qc.cx(bu0, ancilla)
