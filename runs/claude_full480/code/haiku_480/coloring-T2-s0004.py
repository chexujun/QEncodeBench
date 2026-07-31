from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Edges in the graph: (0,2), (1,2), (1,3), (1,4), (3,4)
    edges = [(0, 2), (1, 2), (1, 3), (1, 4), (3, 4)]
    
    # Key insight: For edge (v1, v2) with qubits (a, b, c, d),
    # the 2-bit codes represent different colors iff (a XOR b XOR c XOR d) has odd parity.
    # This is because:
    #   same_color ⟺ (a XOR b) == (c XOR d)
    #   different_color ⟺ (a XOR b) != (c XOR d)
    #   which is true iff a XOR b XOR c XOR d == 1
    
    # Compute parity for each edge and mark violations.
    # Use ancilla_qubits[0] to accumulate violations (0 = all valid, 1 = any invalid).
    # Use ancilla_qubits[1] as temporary for parity computation.
    
    for v1, v2 in edges:
        a = problem_qubits[2*v1]
        b = problem_qubits[2*v1+1]
        c = problem_qubits[2*v2]
        d = problem_qubits[2*v2+1]
        
        # Compute parity: a XOR b XOR c XOR d into ancilla_qubits[1]
        qc.cx(a, ancilla_qubits[1])
        qc.cx(b, ancilla_qubits[1])
        qc.cx(c, ancilla_qubits[1])
        qc.cx(d, ancilla_qubits[1])
        
        # If parity == 0 (invalid edge), flip violation flag
        qc.x(ancilla_qubits[1])
        qc.cx(ancilla_qubits[1], ancilla_qubits[0])
        qc.x(ancilla_qubits[1])
        
        # Uncompute parity (restore ancilla_qubits[1] to 0)
        qc.cx(a, ancilla_qubits[1])
        qc.cx(b, ancilla_qubits[1])
        qc.cx(c, ancilla_qubits[1])
        qc.cx(d, ancilla_qubits[1])
    
    # Apply phase -1 if ancilla_qubits[0] == 0 (all edges valid)
    qc.x(ancilla_qubits[0])
    qc.z(ancilla_qubits[0])
    qc.x(ancilla_qubits[0])
    
    # Uncompute: reverse all steps to restore ancillas to |0>
    for v1, v2 in reversed(edges):
        a = problem_qubits[2*v1]
        b = problem_qubits[2*v1+1]
        c = problem_qubits[2*v2]
        d = problem_qubits[2*v2+1]
        
        qc.cx(a, ancilla_qubits[1])
        qc.cx(b, ancilla_qubits[1])
        qc.cx(c, ancilla_qubits[1])
        qc.cx(d, ancilla_qubits[1])
        
        qc.x(ancilla_qubits[1])
        qc.cx(ancilla_qubits[1], ancilla_qubits[0])
        qc.x(ancilla_qubits[1])
        
        qc.cx(a, ancilla_qubits[1])
        qc.cx(b, ancilla_qubits[1])
        qc.cx(c, ancilla_qubits[1])
        qc.cx(d, ancilla_qubits[1])
