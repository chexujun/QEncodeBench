from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    bad = ancilla_qubits[0:4]
    edge_invalid = ancilla_qubits[4]
    result = ancilla_qubits[5]
    
    edges = [(0, 1), (0, 2), (0, 3), (1, 3), (2, 3)]
    
    # Compute bad[v] for each vertex
    # bad[v] = 1 iff vertex v encodes to color 0 (2-bit code is 00 or 11)
    for v in range(4):
        b0 = problem_qubits[2 * v]
        b1 = problem_qubits[2 * v + 1]
        qc.cx(b0, bad[v])
        qc.cx(b1, bad[v])
        qc.x(bad[v])  # bad[v] = NOT(b0 XOR b1), which is 1 iff b0 == b1
    
    # Initialize result = 1 for AND accumulation
    qc.x(result)
    
    # Forward pass: accumulate AND of edge_valid values
    for u, v in edges:
        qc.ccx(bad[u], bad[v], edge_invalid)  # edge_invalid = bad[u] AND bad[v]
        qc.x(edge_invalid)  # Flip to get edge_valid = NOT(bad[u] AND bad[v])
        qc.ccx(edge_invalid, result, result)  # result = result AND edge_valid
        qc.x(edge_invalid)  # Flip back
        qc.ccx(bad[u], bad[v], edge_invalid)  # Uncompute edge_invalid to 0
    
    # Apply phase -1 iff result = 1 (i.e., iff f(x) = 1)
    qc.z(result)
    
    # Backward pass: reverse the AND accumulation
    for u, v in reversed(edges):
        qc.ccx(bad[u], bad[v], edge_invalid)
        qc.x(edge_invalid)
        qc.ccx(edge_invalid, result, result)  # Reverses the AND due to idempotency
        qc.x(edge_invalid)
        qc.ccx(bad[u], bad[v], edge_invalid)
    
    # Uncompute result back to 0
    qc.x(result)
    
    # Uncompute bad[v] for each vertex (reverse order)
    for v in range(3, -1, -1):
        b0 = problem_qubits[2 * v]
        b1 = problem_qubits[2 * v + 1]
        qc.x(bad[v])
        qc.cx(b1, bad[v])
        qc.cx(b0, bad[v])
