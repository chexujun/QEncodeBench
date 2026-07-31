from qiskit import QuantumCircuit

def build_oracle(qc, problem_qubits, ancilla_qubits):
    """
    Grover oracle for vertex cover problem with size constraint k=2.
    Marks states representing valid vertex covers of size <= 2.
    """
    p = problem_qubits  # [0, 1, 2, 3, 4] - problem qubits for vertices
    a = ancilla_qubits  # [5, 6, 7, 8, 9, 10, 11, 12] - ancillas
    
    # Graph edges: (0,1), (0,3), (1,2), (1,3), (1,4)
    edges = [(0, 1), (0, 3), (1, 2), (1, 3), (1, 4)]
    
    # All 3-element subsets of {0,1,2,3,4} for size checking
    triples = [
        (0, 1, 2), (0, 1, 3), (0, 1, 4), (0, 2, 3), (0, 2, 4), (0, 3, 4),
        (1, 2, 3), (1, 2, 4), (1, 3, 4), (2, 3, 4)
    ]
    
    # === COMPUTE PHASE ===
    # a[0]: uncovered_any = 1 iff any edge is uncovered
    # For each edge (u,v), check if both endpoints are 0
    for u, v in edges:
        qc.x(p[u])
        qc.x(p[v])
        qc.ccx(p[u], p[v], a[0])
        qc.x(p[v])
        qc.x(p[u])
    
    # a[1]: size_large = 1 iff there exist 3+ vertices in cover
    # Check each triple; if all three qubits are 1, mark it
    for i, j, k in triples:
        qc.ccx(p[i], p[j], a[2])
        qc.ccx(a[2], p[k], a[1])
        qc.ccx(p[i], p[j], a[2])
    
    # a[3]: good_flag = 1 iff (no edges uncovered) AND (size <= 2)
    # Initialize to 1, then XOR with error flags
    qc.x(a[3])
    qc.cx(a[0], a[3])  # Flip if any edge uncovered
    qc.cx(a[1], a[3])  # Flip if size too large
    
    # === APPLY PHASE ===
    qc.z(a[3])
    
    # === UNCOMPUTE PHASE (mirror of compute) ===
    qc.cx(a[1], a[3])
    qc.cx(a[0], a[3])
    qc.x(a[3])
    
    # Uncompute size_large
    for i, j, k in reversed(triples):
        qc.ccx(p[i], p[j], a[2])
        qc.ccx(a[2], p[k], a[1])
        qc.ccx(p[i], p[j], a[2])
    
    # Uncompute uncovered_any
    for u, v in reversed(edges):
        qc.x(p[u])
        qc.x(p[v])
        qc.ccx(p[u], p[v], a[0])
        qc.x(p[v])
        qc.x(p[u])
