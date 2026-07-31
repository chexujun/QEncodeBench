from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    p = problem_qubits
    a = ancilla_qubits
    
    # result = a[0]: tracks whether current state is a valid vertex cover of size ≤ 3
    result = a[0]
    qc.x(result)  # Initialize to 1
    
    # Check all edges are covered
    # Edge is NOT covered iff both endpoints are 0
    edges = [(0, 2), (0, 4), (1, 3), (2, 3), (3, 4)]
    
    for i, j in edges:
        temp1, temp2 = a[1], a[2]
        
        # Compute NOT x[i] into temp1
        qc.x(temp1)
        qc.cx(p[i], temp1)
        
        # Compute NOT x[j] into temp2
        qc.x(temp2)
        qc.cx(p[j], temp2)
        
        # If both are 1 (edge not covered), flip result to 0
        qc.ccx(temp1, temp2, result)
        
        # Uncompute
        qc.cx(p[j], temp2)
        qc.x(temp2)
        qc.cx(p[i], temp1)
        qc.x(temp1)
    
    # Compute whether cardinality ≥ 4
    card_ge_4 = a[3]
    
    subsets_4 = [
        [0, 1, 2, 3],
        [0, 1, 2, 4],
        [0, 1, 3, 4],
        [0, 2, 3, 4],
        [1, 2, 3, 4],
    ]
    
    for subset in subsets_4:
        subset_and = a[4]
        subset_qubits = [p[i] for i in subset]
        
        # Compute AND of 4-subset using multi-controlled-X
        qc.mcx(subset_qubits, subset_and, [a[5], a[6]])
        
        # Update card_ge_4 with OR: card_ge_4 = card_ge_4 OR subset_and
        qc.x(card_ge_4)
        qc.ccx(card_ge_4, subset_and, card_ge_4)
        qc.x(card_ge_4)
        
        # Uncompute subset_and
        qc.mcx(subset_qubits, subset_and, [a[5], a[6]])
    
    # Flip result if cardinality ≥ 4
    qc.cx(card_ge_4, result)
    
    # Apply phase
    qc.z(result)
    
    # Uncompute in reverse
    qc.cx(card_ge_4, result)
    
    for subset in reversed(subsets_4):
        subset_and = a[4]
        subset_qubits = [p[i] for i in subset]
        
        qc.mcx(subset_qubits, subset_and, [a[5], a[6]])
        
        qc.x(card_ge_4)
        qc.ccx(card_ge_4, subset_and, card_ge_4)
        qc.x(card_ge_4)
        
        qc.mcx(subset_qubits, subset_and, [a[5], a[6]])
    
    for i, j in reversed(edges):
        temp1, temp2 = a[1], a[2]
        
        qc.x(temp1)
        qc.cx(p[i], temp1)
        qc.x(temp2)
        qc.cx(p[j], temp2)
        
        qc.ccx(temp1, temp2, result)
        
        qc.cx(p[j], temp2)
        qc.x(temp2)
        qc.cx(p[i], temp1)
        qc.x(temp1)
    
    qc.x(result)
