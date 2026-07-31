from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 1), (0, 2), (0, 4), (1, 2), (1, 3), (2, 4)]
    
    edge_coverage = ancilla_qubits[0:6]
    all_edges_covered = ancilla_qubits[7]
    popcount_ok = ancilla_qubits[6]
    
    # Compute edge coverage: each ancilla is 1 iff edge is covered
    for i, (u, v) in enumerate(edges):
        a = edge_coverage[i]
        qc.cx(problem_qubits[u], a)
        qc.cx(problem_qubits[v], a)
        qc.ccx(problem_qubits[u], problem_qubits[v], a)
    
    # Compute all_edges_covered = AND of all edge coverage bits
    qc.x(all_edges_covered)
    for e in edge_coverage:
        qc.x(e)
        qc.cx(e, all_edges_covered)
        qc.x(e)
    
    # Compute popcount_ok = NOT(at least 4 bits set)
    qc.x(popcount_ok)
    
    four_subsets = [
        (0, 1, 2, 3),
        (0, 1, 2, 4),
        (0, 1, 3, 4),
        (0, 2, 3, 4),
        (1, 2, 3, 4)
    ]
    
    for subset in four_subsets:
        term_ancilla = ancilla_qubits[8]
        
        qc.x(term_ancilla)
        qc.mcx([problem_qubits[i] for i in subset], term_ancilla)
        
        qc.x(term_ancilla)
        qc.cx(term_ancilla, popcount_ok)
        qc.x(term_ancilla)
        
        qc.mcx([problem_qubits[i] for i in subset], term_ancilla)
        qc.x(term_ancilla)
    
    # Compute f(x) = all_edges_covered AND popcount_ok and apply phase
    final_oracle = ancilla_qubits[8]
    qc.ccx(all_edges_covered, popcount_ok, final_oracle)
    qc.z(final_oracle)
    qc.ccx(all_edges_covered, popcount_ok, final_oracle)
    
    # Uncompute popcount_ok
    for subset in reversed(four_subsets):
        term_ancilla = ancilla_qubits[8]
        
        qc.x(term_ancilla)
        qc.mcx([problem_qubits[i] for i in subset], term_ancilla)
        
        qc.x(term_ancilla)
        qc.cx(term_ancilla, popcount_ok)
        qc.x(term_ancilla)
        
        qc.mcx([problem_qubits[i] for i in subset], term_ancilla)
        qc.x(term_ancilla)
    
    qc.x(popcount_ok)
    
    # Uncompute all_edges_covered
    for e in reversed(edge_coverage):
        qc.x(e)
        qc.cx(e, all_edges_covered)
        qc.x(e)
    qc.x(all_edges_covered)
    
    # Uncompute edge coverage
    for i in range(len(edges) - 1, -1, -1):
        u, v = edges[i]
        a = edge_coverage[i]
        qc.ccx(problem_qubits[u], problem_qubits[v], a)
        qc.cx(problem_qubits[v], a)
        qc.cx(problem_qubits[u], a)
