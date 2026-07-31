from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 3), (0, 5), (1, 3), (1, 4), (1, 5), (2, 3), (2, 4), (2, 5), (3, 5)]
    five_subsets = [
        [0, 1, 2, 3, 4],
        [0, 1, 2, 3, 5],
        [0, 1, 2, 4, 5],
        [0, 1, 3, 4, 5],
        [0, 2, 3, 4, 5],
        [1, 2, 3, 4, 5]
    ]
    
    # Ancilla allocation
    edge_covered = ancilla_qubits[0:9]
    all_covered = ancilla_qubits[9]
    popcount_gte5 = ancilla_qubits[10]
    phase_flag = ancilla_qubits[11]
    
    # COMPUTE
    
    # Compute edge coverage: edge_covered[i] = problem_qubits[u] OR problem_qubits[v]
    # OR formula in-place: cx(u, r), cx(v, r), ccx(u, v, r)
    for i, (u, v) in enumerate(edges):
        qc.cx(problem_qubits[u], edge_covered[i])
        qc.cx(problem_qubits[v], edge_covered[i])
        qc.ccx(problem_qubits[u], problem_qubits[v], edge_covered[i])
    
    # Compute all_covered = AND of all edge_covered
    qc.mcx(edge_covered, all_covered)
    
    # Compute popcount_gte5: OR of all 5-subsets being all 1
    for subset in five_subsets:
        qc.mcx([problem_qubits[i] for i in subset], phase_flag)
        
        # OR phase_flag into popcount_gte5 using: x, cx, x pattern
        qc.x(popcount_gte5)
        qc.cx(phase_flag, popcount_gte5)
        qc.x(popcount_gte5)
        
        qc.mcx([problem_qubits[i] for i in subset], phase_flag)
    
    # Apply phase: Z to (all_covered AND NOT popcount_gte5)
    qc.x(popcount_gte5)
    qc.ccx(all_covered, popcount_gte5, phase_flag)
    qc.x(popcount_gte5)
    
    qc.z(phase_flag)
    
    # UNCOMPUTE (mirror of compute)
    
    qc.x(popcount_gte5)
    qc.ccx(all_covered, popcount_gte5, phase_flag)
    qc.x(popcount_gte5)
    
    for subset in reversed(five_subsets):
        qc.mcx([problem_qubits[i] for i in subset], phase_flag)
        
        qc.x(popcount_gte5)
        qc.cx(phase_flag, popcount_gte5)
        qc.x(popcount_gte5)
        
        qc.mcx([problem_qubits[i] for i in subset], phase_flag)
    
    qc.mcx(edge_covered, all_covered)
    
    for i in range(len(edges) - 1, -1, -1):
        u, v = edges[i]
        qc.ccx(problem_qubits[u], problem_qubits[v], edge_covered[i])
        qc.cx(problem_qubits[v], edge_covered[i])
        qc.cx(problem_qubits[u], edge_covered[i])
