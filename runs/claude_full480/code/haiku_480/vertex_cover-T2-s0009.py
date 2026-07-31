from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 3), (0, 4), (1, 2), (1, 3), (2, 3), (3, 4)]
    
    # Ancilla allocation
    edge_ancillas = ancilla_qubits[0:6]      # 6 ancillas for edge coverage
    all_edges_covered = ancilla_qubits[6]    # 1 ancilla for AND of edges
    count_flag = ancilla_qubits[7]           # 1 ancilla for popcount >= 4
    temp = ancilla_qubits[8]                 # 1 ancilla for temporary use
    
    # COMPUTE PHASE
    
    # Step 1: Check edge coverage (edge_ancillas[i] = p[u] OR p[v])
    for i, (u, v) in enumerate(edges):
        qc.cx(problem_qubits[u], edge_ancillas[i])
        qc.cx(problem_qubits[v], edge_ancillas[i])
        qc.ccx(problem_qubits[u], problem_qubits[v], edge_ancillas[i])
    
    # Step 2: Compute all_edges_covered = AND of all edge_ancillas
    # Initialize to 1, flip if any edge not covered
    qc.x(all_edges_covered)
    for e in edge_ancillas:
        qc.x(e)
        qc.cx(e, all_edges_covered)
        qc.x(e)
    
    # Step 3: Check if popcount >= 4 using 4-subsets
    four_subsets = [(0, 1, 2, 3), (0, 1, 2, 4), (0, 1, 3, 4), (0, 2, 3, 4), (1, 2, 3, 4)]
    
    qc.x(temp)  # Initialize temp to 1
    
    for subset in four_subsets:
        # Check if all 4 qubits in subset are 1
        for idx in subset:
            qc.x(problem_qubits[idx])
            qc.cx(problem_qubits[idx], temp)
            qc.x(problem_qubits[idx])
        
        # If temp = 1 (all 4 are 1), flip count_flag
        qc.cx(temp, count_flag)
        
        # Restore temp
        for idx in reversed(subset):
            qc.x(problem_qubits[idx])
            qc.cx(problem_qubits[idx], temp)
            qc.x(problem_qubits[idx])
    
    qc.x(temp)  # Restore temp to 0
    
    # count_flag = 1 means popcount >= 4; flip to get popcount <= 3
    qc.x(count_flag)
    
    # Step 4: Combine checks into all_edges_covered
    # Set all_edges_covered = 0 if count_flag = 0 (popcount > 3)
    qc.x(count_flag)
    qc.cx(count_flag, all_edges_covered)
    qc.x(count_flag)
    
    # Step 5: Apply phase
    qc.z(all_edges_covered)
    
    # UNCOMPUTE (reverse order)
    
    qc.x(count_flag)
    qc.cx(count_flag, all_edges_covered)
    qc.x(count_flag)
    
    qc.x(count_flag)
    
    qc.x(temp)
    for subset in reversed(four_subsets):
        for idx in subset:
            qc.x(problem_qubits[idx])
            qc.cx(problem_qubits[idx], temp)
            qc.x(problem_qubits[idx])
        qc.cx(temp, count_flag)
        for idx in reversed(subset):
            qc.x(problem_qubits[idx])
            qc.cx(problem_qubits[idx], temp)
            qc.x(problem_qubits[idx])
    qc.x(temp)
    
    for e in reversed(edge_ancillas):
        qc.x(e)
        qc.cx(e, all_edges_covered)
        qc.x(e)
    qc.x(all_edges_covered)
    
    for i in range(len(edges) - 1, -1, -1):
        u, v = edges[i]
        qc.ccx(problem_qubits[u], problem_qubits[v], edge_ancillas[i])
        qc.cx(problem_qubits[v], edge_ancillas[i])
        qc.cx(problem_qubits[u], edge_ancillas[i])
