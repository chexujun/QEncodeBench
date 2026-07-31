from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 2), (1, 3), (1, 4), (2, 4), (3, 4)]
    
    temp_u, temp_v = ancilla_qubits[5], ancilla_qubits[6]
    
    # Compute edge coverage flags: ec[i] = 1 if edge i is covered
    ec = []
    for idx, (u, v) in enumerate(edges):
        ec_flag = ancilla_qubits[idx]
        ec.append(ec_flag)
        # Compute (NOT x_u) AND (NOT x_v), then negate to get x_u OR x_v
        qc.x(temp_u)
        qc.cx(problem_qubits[u], temp_u)
        qc.x(temp_v)
        qc.cx(problem_qubits[v], temp_v)
        qc.ccx(temp_u, temp_v, ec_flag)
        qc.x(ec_flag)
        qc.cx(problem_qubits[v], temp_v)
        qc.cx(problem_qubits[u], temp_u)
    
    # Compute AND chain for edges
    and_01 = ancilla_qubits[7]
    qc.ccx(ec[0], ec[1], and_01)
    and_012 = ancilla_qubits[5]
    qc.ccx(and_01, ec[2], and_012)
    and_0123 = ancilla_qubits[6]
    qc.ccx(and_012, ec[3], and_0123)
    edges_ok = ancilla_qubits[5]
    # Reuse ancilla[5] for final result
    qc.cx(ancilla_qubits[5], ancilla_qubits[5])  # Clear it (no-op for now)
    qc.ccx(and_0123, ec[4], edges_ok)
    
    # Compute popcount <= 3 by checking NOT (popcount >= 4)
    # popcount >= 4 iff (all 5 are 1) OR (exactly 4 are 1)
    # all_5 = x0 AND x1 AND x2 AND x3 AND x4
    all_5 = ancilla_qubits[6]
    qc.ccx(problem_qubits[0], problem_qubits[1], all_5)
    temp_and = ancilla_qubits[7]
    qc.ccx(all_5, problem_qubits[2], temp_and)
    qc.cx(temp_and, all_5)
    qc.ccx(all_5, problem_qubits[3], temp_and)
    qc.cx(temp_and, all_5)
    qc.ccx(all_5, problem_qubits[4], temp_and)
    qc.cx(temp_and, all_5)
    
    # For exactly 4: compute (NOT x_i) AND (all others)
    exactly_4 = ancilla_qubits[7]
    for i in range(5):
        qc.x(problem_qubits[i])
        not_i_and_rest = ancilla_qubits[6]
        qc.ccx(problem_qubits[i], problem_qubits[(i+1)%5], not_i_and_rest)
        # Continue AND chain
        for j in range(2, 5):
            idx = (i + j) % 5
            qc.ccx(not_i_and_rest, problem_qubits[idx], temp_and)
            qc.cx(temp_and, not_i_and_rest)
            qc.ccx(not_i_and_rest, problem_qubits[idx], temp_and)
        qc.cx(not_i_and_rest, exactly_4)
        qc.x(problem_qubits[i])
    
    # popcount_ge_4 = all_5 OR exactly_4
    popcount_ge_4 = ancilla_qubits[6]
    qc.cx(all_5, popcount_ge_4)
    qc.cx(exactly_4, popcount_ge_4)
    size_ok = popcount_ge_4
    qc.x(size_ok)
    
    # Final predicate: f(x) = edges_ok AND size_ok
    f_x = ancilla_qubits[5]
    qc.ccx(edges_ok, size_ok, f_x)
    
    # Apply phase
    qc.z(f_x)
    
    # Uncompute (reverse order of compute)
    qc.ccx(edges_ok, size_ok, f_x)
    qc.x(size_ok)
    qc.cx(exactly_4, popcount_ge_4)
    qc.cx(all_5, popcount_ge_4)
    for i in range(4, -1, -1):
        qc.x(problem_qubits[i])
        qc.ccx(problem_qubits[i], problem_qubits[(i+1)%5], temp_and)
        qc.x(problem_qubits[i])
    qc.ccx(all_5, problem_qubits[4], temp_and)
    qc.cx(temp_and, all_5)
    qc.ccx(all_5, problem_qubits[3], temp_and)
    qc.cx(temp_and, all_5)
    qc.ccx(all_5, problem_qubits[2], temp_and)
    qc.cx(temp_and, all_5)
    qc.ccx(problem_qubits[0], problem_qubits[1], all_5)
    
    qc.ccx(and_0123, ec[4], edges_ok)
    qc.ccx(and_012, ec[3], and_0123)
    qc.ccx(and_01, ec[2], and_012)
    qc.ccx(ec[0], ec[1], and_01)
    
    for idx in range(4, -1, -1):
        u, v = edges[idx]
        ec_flag = ec[idx]
        qc.x(ec_flag)
        qc.cx(problem_qubits[v], temp_v)
        qc.cx(problem_qubits[u], temp_u)
        qc.ccx(temp_u, temp_v, ec_flag)
        qc.x(temp_v)
        qc.cx(problem_qubits[v], temp_v)
        qc.x(temp_u)
        qc.cx(problem_qubits[u], temp_u)
