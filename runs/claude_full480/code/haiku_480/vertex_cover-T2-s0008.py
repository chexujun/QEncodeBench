from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    p = problem_qubits
    a = ancilla_qubits
    
    edges = [(0,1), (0,3), (1,2), (1,3), (2,3), (2,4)]
    subsets = [[0,1,2,3], [0,1,2,4], [0,1,3,4], [0,2,3,4], [1,2,3,4]]
    
    # Compute: a[0] = 1 iff all edges are covered
    # For each edge (i,j), if both endpoints are 0 (edge uncovered), flip a[0]
    qc.x(a[0])
    for i, j in edges:
        qc.x(p[i])
        qc.x(p[j])
        qc.mcx([p[i], p[j]], a[0])
        qc.x(p[i])
        qc.x(p[j])
    
    # Compute: a[1] = 1 iff popcount >= 4
    # For each 4-subset of vertices, if all 4 are in the cover, flip a[1]
    for subset in subsets:
        qc.mcx([p[i] for i in subset], a[1])
    
    # Compute: a[7] = a[0] AND NOT a[1]
    # This marks valid states: all edges covered AND popcount <= 3
    qc.x(a[1])
    qc.mcx([a[0], a[1]], a[7])
    qc.x(a[1])
    
    # Apply phase -1 to marked states
    qc.z(a[7])
    
    # Uncompute a[7]
    qc.x(a[1])
    qc.mcx([a[0], a[1]], a[7])
    qc.x(a[1])
    
    # Uncompute a[1]
    for subset in reversed(subsets):
        qc.mcx([p[i] for i in subset], a[1])
    
    # Uncompute a[0]
    for i, j in reversed(edges):
        qc.x(p[i])
        qc.x(p[j])
        qc.mcx([p[i], p[j]], a[0])
        qc.x(p[i])
        qc.x(p[j])
    qc.x(a[0])
