from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    """
    Grover oracle for vertex cover on graph with edges:
    (0,2), (0,4), (1,2), (1,3), (1,4), (2,3)
    
    Applies phase -1 iff the configuration is a valid vertex cover with size <= 3.
    """
    edges = [(0, 2), (0, 4), (1, 2), (1, 3), (1, 4), (2, 3)]
    
    # === COMPUTE: Edge coverage ===
    # For each edge (u,v), compute ancilla[i] = x[u] OR x[v]
    # Using identity: OR(a,b) = a XOR b XOR (a AND b)
    for i, (u, v) in enumerate(edges):
        anc = ancilla_qubits[i]
        qc.ccx(problem_qubits[u], problem_qubits[v], anc)  # anc = x[u] AND x[v]
        qc.cx(problem_qubits[u], anc)                       # anc ^= x[u]
        qc.cx(problem_qubits[v], anc)                       # anc ^= x[v] => OR result
    
    # === COMPUTE: Size constraint (popcount <= 3) ===
    # Compute size_invalid = 1 iff popcount >= 4
    # This is true iff at least one of the 6 combinations of 4+ bits are all 1
    size_invalid = ancilla_qubits[6]
    temp_and = ancilla_qubits[7]
    
    # Check all 4-bit subsets (5 such subsets) and the 5-bit subset (1 subset)
    # Use OR to combine them into size_invalid
    four_bit_combos = [
        [0, 1, 2, 3],  # missing bit 4
        [0, 1, 2, 4],  # missing bit 3
        [0, 1, 3, 4],  # missing bit 2
        [0, 2, 3, 4],  # missing bit 1
        [1, 2, 3, 4],  # missing bit 0
    ]
    
    for bits in four_bit_combos:
        # Compute AND of selected problem qubits into temp_and
        qc.ccx(problem_qubits[bits[0]], problem_qubits[bits[1]], temp_and)
        qc.ccx(temp_and, problem_qubits[bits[2]], temp_and)
        qc.ccx(temp_and, problem_qubits[bits[3]], temp_and)
        # OR temp_and into size_invalid
        qc.cx(temp_and, size_invalid)
        # Uncompute temp_and
        qc.ccx(temp_and, problem_qubits[bits[3]], temp_and)
        qc.ccx(temp_and, problem_qubits[bits[2]], temp_and)
        qc.ccx(temp_and, problem_qubits[bits[1]], temp_and)
    
    # Check all 5 bits
    qc.ccx(problem_qubits[0], problem_qubits[1], temp_and)
    qc.ccx(temp_and, problem_qubits[2], temp_and)
    qc.ccx(temp_and, problem_qubits[3], temp_and)
    qc.ccx(temp_and, problem_qubits[4], temp_and)
    qc.cx(temp_and, size_invalid)
    qc.ccx(temp_and, problem_qubits[4], temp_and)
    qc.ccx(temp_and, problem_qubits[3], temp_and)
    qc.ccx(temp_and, problem_qubits[2], temp_and)
    qc.ccx(temp_and, problem_qubits[1], temp_and)
    
    # size_invalid now = 1 iff popcount >= 4; flip to get size_valid
    qc.x(size_invalid)
    
    # === COMPUTE: Final predicate = (all edges covered) AND (size valid) ===
    # all edges covered = edge_ancillas[0] AND ... AND edge_ancillas[5]
    # Use cascading AND into temporary ancillas
    
    and_acc = ancilla_qubits[8]
    
    # Compute AND of all 6 edge coverage bits
    qc.ccx(ancilla_qubits[0], ancilla_qubits[1], temp_and)
    qc.ccx(temp_and, ancilla_qubits[2], and_acc)
    # Swap to continue accumulation
    qc.ccx(and_acc, ancilla_qubits[3], temp_and)
    qc.ccx(temp_and, ancilla_qubits[4], and_acc)
    qc.ccx(and_acc, ancilla_qubits[5], temp_and)
    # temp_and = all edges covered; and_acc is free
    
    # Final predicate: (all edges covered) AND (size valid)
    qc.ccx(temp_and, size_invalid, and_acc)
    # and_acc now contains the final predicate
    
    # === Apply phase ===
    qc.z(and_acc)
    
    # === UNCOMPUTE in reverse ===
    # Uncompute final AND
    qc.ccx(temp_and, size_invalid, and_acc)
    qc.ccx(and_acc, ancilla_qubits[5], temp_and)
    qc.ccx(temp_and, ancilla_qubits[4], and_acc)
    qc.ccx(and_acc, ancilla_qubits[3], temp_and)
    qc.ccx(temp_and, ancilla_qubits[2], and_acc)
    qc.ccx(and_acc, ancilla_qubits[1], temp_and)
    qc.ccx(temp_and, ancilla_qubits[0], and_acc)
    
    # Uncompute size_invalid
    qc.x(size_invalid)
    
    # Uncompute 5-bit AND (reverse order)
    qc.ccx(temp_and, problem_qubits[1], temp_and)
    qc.ccx(temp_and, problem_qubits[2], temp_and)
    qc.ccx(temp_and, problem_qubits[3], temp_and)
    qc.ccx(temp_and, problem_qubits[4], temp_and)
    qc.cx(temp_and, size_invalid)
    qc.ccx(temp_and, problem_qubits[4], temp_and)
    qc.ccx(temp_and, problem_qubits[3], temp_and)
    qc.ccx(temp_and, problem_qubits[2], temp_and)
    qc.ccx(temp_and, problem_qubits[1], temp_and)
    
    # Uncompute 4-bit ANDs (in reverse order)
    for bits in reversed(four_bit_combos):
        qc.ccx(temp_and, problem_qubits[bits[1]], temp_and)
        qc.cx(temp_and, size_invalid)
        qc.ccx(temp_and, problem_qubits[bits[3]], temp_and)
        qc.ccx(temp_and, problem_qubits[bits[2]], temp_and)
        qc.ccx(temp_and, problem_qubits[bits[0]], temp_and)
    
    # Uncompute edge coverage (mirror of compute)
    for i in range(len(edges) - 1, -1, -1):
        u, v = edges[i]
        anc = ancilla_qubits[i]
        qc.cx(problem_qubits[v], anc)
        qc.cx(problem_qubits[u], anc)
        qc.ccx(problem_qubits[u], problem_qubits[v], anc)
