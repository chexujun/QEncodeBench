from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 1), (1, 4), (1, 5), (2, 3), (2, 5), (3, 5)]
    p = problem_qubits
    a = ancilla_qubits
    
    # COMPUTE PHASE
    
    # Part 1: Compute edge uncovered flags
    # a[i] = 1 iff edge i has both endpoints at 0 (is uncovered)
    for idx, (i, j) in enumerate(edges):
        qc.x(p[i])
        qc.x(p[j])
        qc.ccx(p[i], p[j], a[idx])
        qc.x(p[j])
        qc.x(p[i])
    
    # Part 2: Compute any_uncovered = OR(a[0], a[1], ..., a[5])
    # Using: OR(bits) = NOT(AND(NOT bits))
    for i in range(6):
        qc.x(a[i])
    
    qc.ccx(a[0], a[1], a[7])
    qc.ccx(a[7], a[2], a[8])
    qc.ccx(a[8], a[3], a[7])
    qc.ccx(a[7], a[4], a[8])
    qc.ccx(a[8], a[5], a[6])
    qc.x(a[6])
    
    qc.ccx(a[8], a[5], a[6])
    qc.ccx(a[7], a[4], a[8])
    qc.ccx(a[8], a[3], a[7])
    qc.ccx(a[7], a[2], a[8])
    qc.ccx(a[0], a[1], a[7])
    
    for i in range(6):
        qc.x(a[i])
    
    # Part 3: Compute popcount >= 4
    # Check if any 4 problem qubits are all 1
    combos = [
        (0,1,2,3), (0,1,2,4), (0,1,2,5), (0,1,3,4), (0,1,3,5), (0,1,4,5),
        (0,2,3,4), (0,2,3,5), (0,2,4,5), (0,3,4,5),
        (1,2,3,4), (1,2,3,5), (1,2,4,5), (1,3,4,5), (2,3,4,5)
    ]
    
    for (i, j, k, l) in combos:
        qc.ccx(p[i], p[j], a[0])
        qc.ccx(p[k], p[l], a[1])
        qc.ccx(a[0], a[1], a[2])
        qc.cx(a[2], a[8])
        qc.ccx(a[0], a[1], a[2])
        qc.ccx(p[k], p[l], a[1])
        qc.ccx(p[i], p[j], a[0])
    
    # Part 4: Apply phase if (NOT any_uncovered) AND (NOT popcount_over_3)
    qc.x(a[6])
    qc.x(a[8])
    qc.ccx(a[6], a[8], a[0])
    qc.z(a[0])
    qc.ccx(a[6], a[8], a[0])
    qc.x(a[8])
    qc.x(a[6])
    
    # UNCOMPUTE PHASE
    
    # Uncompute popcount >= 4
    for (i, j, k, l) in reversed(combos):
        qc.ccx(p[i], p[j], a[0])
        qc.ccx(p[k], p[l], a[1])
        qc.ccx(a[0], a[1], a[2])
        qc.cx(a[2], a[8])
        qc.ccx(a[0], a[1], a[2])
        qc.ccx(p[k], p[l], a[1])
        qc.ccx(p[i], p[j], a[0])
    
    # Uncompute any_uncovered
    for i in range(6):
        qc.x(a[i])
    
    qc.ccx(a[0], a[1], a[7])
    qc.ccx(a[7], a[2], a[8])
    qc.ccx(a[8], a[3], a[7])
    qc.ccx(a[7], a[4], a[8])
    qc.ccx(a[8], a[5], a[6])
    qc.x(a[6])
    
    qc.ccx(a[8], a[5], a[6])
    qc.ccx(a[7], a[4], a[8])
    qc.ccx(a[8], a[3], a[7])
    qc.ccx(a[7], a[2], a[8])
    qc.ccx(a[0], a[1], a[7])
    
    for i in range(6):
        qc.x(a[i])
    
    # Uncompute edge uncovered flags
    for idx in range(5, -1, -1):
        i, j = edges[idx]
        qc.x(p[i])
        qc.x(p[j])
        qc.ccx(p[i], p[j], a[idx])
        qc.x(p[j])
        qc.x(p[i])
