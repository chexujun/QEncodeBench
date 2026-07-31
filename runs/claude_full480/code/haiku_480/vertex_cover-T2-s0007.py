from qiskit import QuantumCircuit
from itertools import combinations

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    """
    Oracle for vertex cover of size at most 2.
    Graph edges: (0,3), (1,2), (1,3), (2,4)
    Marks states where every edge is covered and the cover has size <= 2.
    """
    x = problem_qubits
    a = ancilla_qubits
    
    edges = [(0, 3), (1, 2), (1, 3), (2, 4)]
    
    # === COMPUTE PHASE ===
    
    # Step 1: Compute edge coverage for each edge
    # a[idx] = 1 iff edge idx is covered (x[u] OR x[v])
    for idx, (u, v) in enumerate(edges):
        qc.x(a[idx])  # Initialize to 1
        qc.x(x[u])
        qc.x(x[v])
        qc.ccx(x[u], x[v], a[idx])  # Flip if NOT x[u] AND NOT x[v]
        qc.x(x[v])
        qc.x(x[u])
    
    # Step 2: Compute popcount >= 3
    # a[4] = 1 iff popcount(x) >= 3
    for i, j, k in combinations(range(5), 3):
        qc.mcx([x[i], x[j], x[k]], a[4])
    
    # Step 3: AND all edge coverage bits
    # a[5] = 1 iff all edges are covered
    qc.mcx(a[0:4], a[5])
    
    # Step 4: Compute final predicate
    # a[6] = 1 iff (all edges covered) AND (popcount <= 2)
    #      = (a[5]) AND (NOT a[4])
    qc.x(a[4])
    qc.ccx(a[5], a[4], a[6])
    qc.x(a[4])
    
    # Step 5: Apply phase
    qc.z(a[6])
    
    # === UNCOMPUTE PHASE ===
    
    # Reverse step 4
    qc.x(a[4])
    qc.ccx(a[5], a[4], a[6])
    qc.x(a[4])
    
    # Reverse step 3
    qc.mcx(a[0:4], a[5])
    
    # Reverse step 2
    for i, j, k in combinations(range(5), 3):
        qc.mcx([x[i], x[j], x[k]], a[4])
    
    # Reverse step 1
    for idx, (u, v) in enumerate(edges):
        qc.x(x[u])
        qc.x(x[v])
        qc.ccx(x[u], x[v], a[idx])
        qc.x(x[v])
        qc.x(x[u])
        qc.x(a[idx])  # Restore to 0
