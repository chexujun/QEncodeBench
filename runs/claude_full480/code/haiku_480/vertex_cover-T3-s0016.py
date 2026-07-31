def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0,2), (0,3), (1,3), (1,5), (2,3), (3,4), (3,5), (4,5)]
    
    # Ancilla allocation
    edge_not_covered = ancilla_qubits[0:8]
    any_uncovered = ancilla_qubits[8]
    work = ancilla_qubits[9]
    popcount_gt3 = ancilla_qubits[10]
    
    # COMPUTE PHASE
    
    # Step 1: Compute "edge NOT covered" for each edge
    # edge_not_covered[i] = (NOT p[u]) AND (NOT p[v])
    for i, (u, v) in enumerate(edges):
        qc.x(problem_qubits[u])
        qc.x(problem_qubits[v])
        qc.ccx(problem_qubits[u], problem_qubits[v], edge_not_covered[i])
        qc.x(problem_qubits[v])
        qc.x(problem_qubits[u])
    
    # Step 2: Compute any_uncovered = OR(edge_not_covered[0..7])
    for i in range(8):
        qc.x(any_uncovered)
        qc.x(edge_not_covered[i])
        qc.ccx(any_uncovered, edge_not_covered[i], work)
        qc.x(edge_not_covered[i])
        qc.x(any_uncovered)
        qc.x(work)
        qc.cx(work, any_uncovered)
        qc.x(work)
    
    # Step 3: Compute popcount_gt3 = 1 iff popcount > 3
    # Check all 4-subsets; if any all-1, then popcount >= 4
    four_combs = [
        (0,1,2,3), (0,1,2,4), (0,1,2,5), (0,1,3,4), (0,1,3,5), (0,1,4,5),
        (0,2,3,4), (0,2,3,5), (0,2,4,5), (0,3,4,5),
        (1,2,3,4), (1,2,3,5), (1,2,4,5), (1,3,4,5),
        (2,3,4,5)
    ]
    
    for combo in four_combs:
        qc.mcx([problem_qubits[i] for i in combo], popcount_gt3)
    
    # Step 4: Apply phase -1 iff (all edges covered) AND (popcount <= 3)
    # Flip ancillas: any_uncovered=1 means all covered; popcount_gt3=1 means <=3
    qc.x(any_uncovered)
    qc.x(popcount_gt3)
    
    # Mark the state with Z gate
    qc.ccx(any_uncovered, popcount_gt3, work)
    qc.z(work)
    qc.ccx(any_uncovered, popcount_gt3, work)
    
    # Uncompute the flips
    qc.x(popcount_gt3)
    qc.x(any_uncovered)
    
    # UNCOMPUTE PHASE
    
    # Uncompute popcount_gt3
    for combo in reversed(four_combs):
        qc.mcx([problem_qubits[i] for i in combo], popcount_gt3)
    
    # Uncompute any_uncovered (reverse OR loop)
    for i in range(7, -1, -1):
        qc.x(work)
        qc.cx(work, any_uncovered)
        qc.x(work)
        qc.x(any_uncovered)
        qc.x(edge_not_covered[i])
        qc.ccx(any_uncovered, edge_not_covered[i], work)
        qc.x(edge_not_covered[i])
        qc.x(any_uncovered)
    
    # Uncompute edge_not_covered (reverse order)
    for i in range(7, -1, -1):
        u, v = edges[i]
        qc.x(problem_qubits[u])
        qc.x(problem_qubits[v])
        qc.ccx(problem_qubits[u], problem_qubits[v], edge_not_covered[i])
        qc.x(problem_qubits[v])
        qc.x(problem_qubits[u])
