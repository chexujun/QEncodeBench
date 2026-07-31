from qiskit import QuantumCircuit
from itertools import combinations

def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    edges = [(0,1), (0,2), (0,4), (1,2), (1,4), (2,3), (2,5), (4,5)]
    
    # Ancilla allocation
    edge_unc = ancilla_qubits[0:8]   # uncovered status per edge
    any_unc = ancilla_qubits[8]      # OR of uncovered edges
    bad_pop = ancilla_qubits[9]      # popcount > 3 flag
    result = ancilla_qubits[10]      # final phase qubit
    
    # === COMPUTE PHASE ===
    
    # Step 1: Mark edges that are uncovered
    # uncovered[i] = (NOT x[u[i]]) AND (NOT x[v[i]])
    for idx, (u, v) in enumerate(edges):
        qc.x(problem_qubits[u])
        qc.x(problem_qubits[v])
        qc.ccx(problem_qubits[u], problem_qubits[v], edge_unc[idx])
        qc.x(problem_qubits[v])
        qc.x(problem_qubits[u])
    
    # Step 2: Compute any_unc = OR(all edge_unc)
    # Using the formula: OR(a,b,c,...) via cascading
    qc.cx(edge_unc[0], any_unc)
    qc.cx(edge_unc[1], any_unc)
    qc.ccx(edge_unc[0], edge_unc[1], any_unc)
    
    for i in range(2, 8):
        qc.cx(edge_unc[i], any_unc)
        qc.ccx(edge_unc[i], any_unc, edge_unc[0])
        qc.cx(edge_unc[0], any_unc)
        qc.ccx(edge_unc[i], any_unc, edge_unc[0])
    
    # Step 3: Check if popcount > 3
    # Mark bad_pop if any 4-subset of problem_qubits are all 1
    four_subsets = list(combinations(range(6), 4))
    for subset in four_subsets:
        qc.mcx([problem_qubits[i] for i in subset], bad_pop)
    
    # Step 4: Compute result = (NOT any_unc) AND (NOT bad_pop)
    # This is set to 1 iff the state should be marked (apply -1 phase)
    qc.x(any_unc)
    qc.x(bad_pop)
    qc.ccx(any_unc, bad_pop, result)
    qc.x(bad_pop)
    qc.x(any_unc)
    
    # === APPLY PHASE ===
    qc.z(result)
    
    # === UNCOMPUTE ===
    
    # Uncompute result
    qc.x(any_unc)
    qc.x(bad_pop)
    qc.ccx(any_unc, bad_pop, result)
    qc.x(bad_pop)
    qc.x(any_unc)
    
    # Uncompute bad_pop
    for subset in four_subsets:
        qc.mcx([problem_qubits[i] for i in subset], bad_pop)
    
    # Uncompute any_unc (reverse of OR computation)
    for i in range(7, 1, -1):
        qc.ccx(edge_unc[i], any_unc, edge_unc[0])
        qc.cx(edge_unc[0], any_unc)
        qc.ccx(edge_unc[i], any_unc, edge_unc[0])
        qc.cx(edge_unc[i], any_unc)
    
    qc.ccx(edge_unc[0], edge_unc[1], any_unc)
    qc.cx(edge_unc[1], any_unc)
    qc.cx(edge_unc[0], any_unc)
    
    # Uncompute edge_unc
    for idx in range(7, -1, -1):
        u, v = edges[idx]
        qc.x(problem_qubits[u])
        qc.x(problem_qubits[v])
        qc.ccx(problem_qubits[u], problem_qubits[v], edge_unc[idx])
        qc.x(problem_qubits[v])
        qc.x(problem_qubits[u])
