from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0,1), (0,2), (1,2), (2,3), (2,4), (3,4)]
    
    edge_anc = ancilla_qubits[0:6]
    all_edges_anc = ancilla_qubits[6]
    popcount_anc = ancilla_qubits[7]
    result_anc = ancilla_qubits[8]
    
    # COMPUTE PHASE:
    
    # Step 1: Compute if each edge is covered (OR of endpoints)
    for i, (a, b) in enumerate(edges):
        qc.x(edge_anc[i])
        qc.x(problem_qubits[a])
        qc.x(problem_qubits[b])
        qc.ccx(problem_qubits[a], problem_qubits[b], edge_anc[i])
        qc.x(problem_qubits[b])
        qc.x(problem_qubits[a])
    
    # Step 2: Compute if all edges are covered (AND of all edge_anc)
    qc.mcx(edge_anc, all_edges_anc)
    
    # Step 3: Compute if popcount > 3 (at least 4 vertices selected)
    subsets = [
        [0, 1, 2, 3],
        [0, 1, 2, 4],
        [0, 1, 3, 4],
        [0, 2, 3, 4],
        [1, 2, 3, 4],
        [0, 1, 2, 3, 4]
    ]
    
    temp = edge_anc[0]
    for subset in subsets:
        qc.mcx([problem_qubits[i] for i in subset], temp)
        qc.cx(temp, popcount_anc)
        qc.mcx([problem_qubits[i] for i in subset], temp)
    
    # Step 4: Compute result = all_edges_anc AND NOT popcount_anc
    qc.x(popcount_anc)
    qc.ccx(all_edges_anc, popcount_anc, result_anc)
    qc.x(popcount_anc)
    
    # Step 5: Apply phase -1 to result_anc = 1 states
    qc.z(result_anc)
    
    # UNCOMPUTE:
    
    # Reverse Step 4
    qc.x(popcount_anc)
    qc.ccx(all_edges_anc, popcount_anc, result_anc)
    qc.x(popcount_anc)
    
    # Reverse Step 3
    temp = edge_anc[0]
    for subset in reversed(subsets):
        qc.mcx([problem_qubits[i] for i in subset], temp)
        qc.cx(temp, popcount_anc)
        qc.mcx([problem_qubits[i] for i in subset], temp)
    
    # Reverse Step 2
    qc.mcx(edge_anc, all_edges_anc)
    
    # Reverse Step 1
    for i in range(5, -1, -1):
        a, b = edges[i]
        qc.x(problem_qubits[a])
        qc.x(problem_qubits[b])
        qc.ccx(problem_qubits[a], problem_qubits[b], edge_anc[i])
        qc.x(problem_qubits[b])
        qc.x(problem_qubits[a])
        qc.x(edge_anc[i])
