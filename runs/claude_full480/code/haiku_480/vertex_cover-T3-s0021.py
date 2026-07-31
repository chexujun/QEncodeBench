from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0,1), (1,2), (1,4), (1,5), (2,3), (2,5), (3,4), (3,5), (4,5)]
    
    # Allocate ancillas
    edge_ancillas = ancilla_qubits[:9]      # 9 ancillas for edge coverage
    all_covered = ancilla_qubits[9]         # AND result for edge coverage
    popcount_ok = ancilla_qubits[10]        # popcount <= 3 check
    and_temp = ancilla_qubits[11]           # temporary for AND reduction
    
    # ===== COMPUTE PHASE =====
    
    # Compute edge coverage: edge_ancillas[i] = problem_qubits[u] OR problem_qubits[v]
    for i, (u, v) in enumerate(edges):
        a, b, c = problem_qubits[u], problem_qubits[v], edge_ancillas[i]
        qc.cx(a, c)           # c = a
        qc.cx(b, c)           # c = a XOR b
        qc.ccx(a, b, c)       # c = (a XOR b) XOR (a AND b) = a OR b
    
    # Compute AND of all edge_ancillas into all_covered
    qc.cx(edge_ancillas[0], all_covered)
    for i in range(1, 9):
        qc.ccx(all_covered, edge_ancillas[i], and_temp)
        qc.cx(and_temp, all_covered)
    
    # Compute popcount <= 3 check into popcount_ok
    qc.x(popcount_ok)  # Initialize to 1 (assume <= 3)
    
    # All 4-qubit combinations of problem_qubits
    combos_4 = [
        (0,1,2,3), (0,1,2,4), (0,1,2,5), (0,1,3,4), (0,1,3,5), (0,1,4,5),
        (0,2,3,4), (0,2,3,5), (0,2,4,5), (0,3,4,5), (1,2,3,4), (1,2,3,5),
        (1,2,4,5), (1,3,4,5), (2,3,4,5)
    ]
    
    # If any 4-qubit combination is all 1, flip popcount_ok to 0
    for (i, j, k, l) in combos_4:
        qc.mcx([problem_qubits[i], problem_qubits[j], problem_qubits[k], problem_qubits[l]], 
                popcount_ok)
    
    # Apply phase -1 if both conditions met (all_covered=1 AND popcount_ok=1)
    qc.cz(all_covered, popcount_ok)
    
    # ===== UNCOMPUTE PHASE =====
    
    # Uncompute popcount_ok
    for (i, j, k, l) in combos_4:
        qc.mcx([problem_qubits[i], problem_qubits[j], problem_qubits[k], problem_qubits[l]], 
                popcount_ok)
    qc.x(popcount_ok)
    
    # Uncompute AND reduction
    for i in range(8, 0, -1):
        qc.cx(and_temp, all_covered)
        qc.ccx(all_covered, edge_ancillas[i], and_temp)
    qc.cx(edge_ancillas[0], all_covered)
    
    # Uncompute edge coverage
    for i, (u, v) in enumerate(edges):
        a, b, c = problem_qubits[u], problem_qubits[v], edge_ancillas[i]
        qc.ccx(a, b, c)
        qc.cx(b, c)
        qc.cx(a, c)
