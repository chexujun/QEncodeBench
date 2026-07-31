from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 3), (0, 4), (1, 3), (1, 4), (2, 4), (3, 4)]
    
    # Ancilla allocation:
    edge_not_covered = ancilla_qubits[0:6]      # [0:6] - one per edge
    all_edges_ok = ancilla_qubits[6]            # [6]
    size_ok = ancilla_qubits[7]                 # [7]
    temp_and = ancilla_qubits[8]                # [8]
    
    # ===== COMPUTE: Edge Coverage =====
    # For each edge (u,v), set edge_not_covered[i] = (NOT u) AND (NOT v)
    # (i.e., edge is uncovered when both endpoints are not in the cover)
    for i, (u, v) in enumerate(edges):
        qc.x(problem_qubits[u])
        qc.x(problem_qubits[v])
        qc.ccx(problem_qubits[u], problem_qubits[v], edge_not_covered[i])
        qc.x(problem_qubits[v])
        qc.x(problem_qubits[u])
    
    # ===== COMPUTE: All edges covered =====
    # all_edges_ok = 1 iff all edge_not_covered[i] = 0
    # Start with all_edges_ok = 1, then accumulate AND of (NOT edge_not_covered[i])
    qc.x(all_edges_ok)
    for i in range(6):
        qc.ccx(all_edges_ok, edge_not_covered[i], all_edges_ok)
    
    # ===== COMPUTE: Size constraint =====
    # size_ok = 1 iff Hamming weight <= 3
    # Check: if any 4-qubit subset is all 1s, then weight > 3 (bad)
    # Subsets of 4: (0,1,2,3), (0,1,2,4), (0,1,3,4), (0,2,3,4), (1,2,3,4)
    
    qc.x(size_ok)  # Initialize size_ok = 1 (good by default)
    
    for combo in [(0, 1, 2, 3), (0, 1, 2, 4), (0, 1, 3, 4), (0, 2, 3, 4), (1, 2, 3, 4)]:
        i0, i1, i2, i3 = combo
        # Compute AND of these 4 problem qubits into temp_and, XOR into size_ok, uncompute
        qc.ccx(problem_qubits[i0], problem_qubits[i1], temp_and)
        qc.ccx(temp_and, problem_qubits[i2], edge_not_covered[0])
        qc.ccx(edge_not_covered[0], problem_qubits[i3], size_ok)
        # Uncompute
        qc.ccx(edge_not_covered[0], problem_qubits[i3], size_ok)
        qc.ccx(temp_and, problem_qubits[i2], edge_not_covered[0])
        qc.ccx(problem_qubits[i0], problem_qubits[i1], temp_and)
    
    # ===== PHASE: Apply -1 to valid solutions =====
    # valid = all_edges_ok AND size_ok
    # Compute: size_ok = size_ok AND all_edges_ok (overwrite size_ok)
    qc.ccx(all_edges_ok, size_ok, size_ok)
    
    # Apply phase -1 if size_ok = 1
    qc.z(size_ok)
    
    # ===== UNCOMPUTE: Reverse phase setup =====
    qc.ccx(all_edges_ok, size_ok, size_ok)
    
    # ===== UNCOMPUTE: Size constraint =====
    for combo in [(1, 2, 3, 4), (0, 2, 3, 4), (0, 1, 3, 4), (0, 1, 2, 4), (0, 1, 2, 3)]:
        i0, i1, i2, i3 = combo
        qc.ccx(problem_qubits[i0], problem_qubits[i1], temp_and)
        qc.ccx(temp_and, problem_qubits[i2], edge_not_covered[0])
        qc.ccx(edge_not_covered[0], problem_qubits[i3], size_ok)
        qc.ccx(temp_and, problem_qubits[i2], edge_not_covered[0])
        qc.ccx(problem_qubits[i0], problem_qubits[i1], temp_and)
    
    qc.x(size_ok)
    
    # ===== UNCOMPUTE: All edges covered =====
    for i in range(5, -1, -1):
        qc.ccx(all_edges_ok, edge_not_covered[i], all_edges_ok)
    qc.x(all_edges_ok)
    
    # ===== UNCOMPUTE: Edge coverage =====
    for i in range(5, -1, -1):
        u, v = edges[i]
        qc.x(problem_qubits[u])
        qc.x(problem_qubits[v])
        qc.ccx(problem_qubits[u], problem_qubits[v], edge_not_covered[i])
        qc.x(problem_qubits[v])
        qc.x(problem_qubits[u])
