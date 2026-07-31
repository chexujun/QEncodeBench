def build_oracle(qc, problem_qubits, ancilla_qubits):
    edges = [(0,2), (0,4), (0,5), (1,2), (1,3), (1,5), (2,4), (2,5), (4,5)]
    
    # Ancilla allocation
    edge_uncovered = ancilla_qubits[0:9]  # One per edge
    edges_all_covered = ancilla_qubits[9]
    popcount_exceeds_4 = ancilla_qubits[10]
    result = ancilla_qubits[11]
    
    # COMPUTE PHASE
    
    # Step 1: For each edge, mark if it's not covered (both endpoints are 0)
    for i, (u, v) in enumerate(edges):
        qc.x(problem_qubits[u])
        qc.x(problem_qubits[v])
        qc.ccx(problem_qubits[u], problem_qubits[v], edge_uncovered[i])
        qc.x(problem_qubits[v])
        qc.x(problem_qubits[u])
    
    # Step 2: Check all edges covered (none of the "uncovered" bits are set)
    # This is: NOT(OR(edge_uncovered)) = AND(NOT(edge_uncovered[i]))
    for i in range(9):
        qc.x(edge_uncovered[i])
    qc.mcx(edge_uncovered, edges_all_covered)
    for i in range(9):
        qc.x(edge_uncovered[i])
    
    # Step 3: Check popcount <= 4 (equivalently, NOT(popcount > 4))
    # Popcount > 4 means popcount ∈ {5, 6}
    
    # Check popcount == 6 (all ones)
    temp_pop6 = ancilla_qubits[0]
    qc.mcx(problem_qubits, temp_pop6)
    
    # Check popcount == 5 (exactly one zero)
    temp_pop5 = ancilla_qubits[1]
    for i in range(6):
        # Check if qubit i is 0 and all others are 1
        qc.x(problem_qubits[i])
        other_qubits = [problem_qubits[j] for j in range(6) if j != i]
        temp_and = ancilla_qubits[2]
        qc.mcx(other_qubits, temp_and)
        
        # OR temp_and into temp_pop5
        qc.x(temp_pop5)
        qc.x(temp_and)
        qc.ccx(temp_pop5, temp_and, ancilla_qubits[3])
        qc.x(temp_and)
        qc.x(temp_pop5)
        qc.x(ancilla_qubits[3])
        qc.cx(ancilla_qubits[3], temp_pop5)
        qc.x(ancilla_qubits[3])
        
        qc.mcx(other_qubits, temp_and)
        qc.x(problem_qubits[i])
    
    # OR temp_pop6 and temp_pop5 to get popcount_exceeds
    qc.x(temp_pop5)
    qc.x(temp_pop6)
    qc.ccx(temp_pop5, temp_pop6, ancilla_qubits[3])
    qc.x(temp_pop6)
    qc.x(temp_pop5)
    qc.x(ancilla_qubits[3])
    qc.cx(ancilla_qubits[3], popcount_exceeds_4)
    qc.x(ancilla_qubits[3])
    
    # Step 4: Combine conditions
    # result = edges_all_covered AND NOT(popcount_exceeds_4)
    qc.x(popcount_exceeds_4)
    qc.ccx(edges_all_covered, popcount_exceeds_4, result)
    
    # Step 5: Apply phase oracle
    qc.z(result)
    
    # UNCOMPUTE PHASE (reverse order)
    
    qc.ccx(edges_all_covered, popcount_exceeds_4, result)
    qc.x(popcount_exceeds_4)
    
    # Undo OR
    qc.x(temp_pop5)
    qc.x(temp_pop6)
    qc.ccx(temp_pop5, temp_pop6, ancilla_qubits[3])
    qc.x(temp_pop6)
    qc.x(temp_pop5)
    qc.x(ancilla_qubits[3])
    qc.cx(ancilla_qubits[3], popcount_exceeds_4)
    qc.x(ancilla_qubits[3])
    
    # Undo popcount checks
    for i in range(5, -1, -1):
        qc.x(problem_qubits[i])
        other_qubits = [problem_qubits[j] for j in range(6) if j != i]
        temp_and = ancilla_qubits[2]
        qc.mcx(other_qubits, temp_and)
        
        qc.x(temp_pop5)
        qc.x(temp_and)
        qc.ccx(temp_pop5, temp_and, ancilla_qubits[3])
        qc.x(temp_and)
        qc.x(temp_pop5)
        qc.x(ancilla_qubits[3])
        qc.cx(ancilla_qubits[3], temp_pop5)
        qc.x(ancilla_qubits[3])
        
        qc.mcx(other_qubits, temp_and)
        qc.x(problem_qubits[i])
    
    qc.mcx(problem_qubits, temp_pop6)
    
    # Undo edges_all_covered
    for i in range(9):
        qc.x(edge_uncovered[i])
    qc.mcx(edge_uncovered, edges_all_covered)
    for i in range(9):
        qc.x(edge_uncovered[i])
    
    # Undo edge_uncovered
    for i in range(8, -1, -1):
        u, v = edges[i]
        qc.x(problem_qubits[u])
        qc.x(problem_qubits[v])
        qc.ccx(problem_qubits[u], problem_qubits[v], edge_uncovered[i])
        qc.x(problem_qubits[v])
        qc.x(problem_qubits[u])
