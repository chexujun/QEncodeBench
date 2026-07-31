from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0,3), (1,2), (2,3), (2,4), (2,5), (3,4)]
    a = ancilla_qubits
    
    # === COMPUTE ===
    
    # Step 1: Mark each edge that is NOT covered (both endpoints are 0)
    edge_not_covered = a[0:6]
    for idx, (u, v) in enumerate(edges):
        qc.x(problem_qubits[u])
        qc.x(problem_qubits[v])
        qc.ccx(problem_qubits[u], problem_qubits[v], edge_not_covered[idx])
        qc.x(problem_qubits[v])
        qc.x(problem_qubits[u])
    
    # Step 2: Compute if popcount >= 3 (mark into ancilla a[6])
    at_least_3 = a[6]
    temp = a[7]
    
    # Iterate through all C(6,3)=20 triplets and OR together
    triplets = [
        (0,1,2), (0,1,3), (0,1,4), (0,1,5),
        (0,2,3), (0,2,4), (0,2,5),
        (0,3,4), (0,3,5), (0,4,5),
        (1,2,3), (1,2,4), (1,2,5),
        (1,3,4), (1,3,5), (1,4,5),
        (2,3,4), (2,3,5), (2,4,5),
        (3,4,5),
    ]
    
    for i, j, k in triplets:
        # Compute (problem_qubits[i] AND problem_qubits[j]) into temp
        qc.ccx(problem_qubits[i], problem_qubits[j], temp)
        # OR (temp AND problem_qubits[k]) into at_least_3
        qc.x(at_least_3)
        qc.ccx(temp, problem_qubits[k], at_least_3)
        qc.x(at_least_3)
        # Uncompute temp
        qc.ccx(problem_qubits[i], problem_qubits[j], temp)
    
    # === PHASE ===
    
    # Apply Z-phase when: (all edges are covered) AND (popcount <= 2)
    # = (all edge_not_covered are 0) AND (at_least_3 is 0)
    # Use negated multi-controlled-X (via H gates) to implement multi-controlled-Z
    
    # Invert ancilla controls to mark when conditions are met
    for i in range(6):
        qc.x(edge_not_covered[i])
    qc.x(at_least_3)
    
    # Apply controlled phase: H, mcx, H pattern
    flag = a[8]
    controls = edge_not_covered.tolist() + [at_least_3]
    qc.h(flag)
    qc.mcx(controls, flag)
    qc.h(flag)
    
    # Restore ancilla controls
    for i in range(6):
        qc.x(edge_not_covered[i])
    qc.x(at_least_3)
    
    # === UNCOMPUTE ===
    
    # Uncompute at_least_3 (in reverse)
    for i, j, k in reversed(triplets):
        qc.ccx(problem_qubits[i], problem_qubits[j], temp)
        qc.x(at_least_3)
        qc.ccx(temp, problem_qubits[k], at_least_3)
        qc.x(at_least_3)
        qc.ccx(problem_qubits[i], problem_qubits[j], temp)
    
    # Uncompute edge_not_covered (in reverse)
    for idx in range(5, -1, -1):
        u, v = edges[idx]
        qc.x(problem_qubits[u])
        qc.x(problem_qubits[v])
        qc.ccx(problem_qubits[u], problem_qubits[v], edge_not_covered[idx])
        qc.x(problem_qubits[v])
        qc.x(problem_qubits[u])
