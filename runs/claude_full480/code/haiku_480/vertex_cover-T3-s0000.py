from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0,1), (0,4), (1,2), (1,3), (1,4), (1,5), (2,5), (3,4)]
    k = 4
    
    # Ancilla partition:
    # [0-7]: one per edge to check coverage
    # [8-10]: popcount bits
    # [11]: validity flag
    
    # COMPUTE PHASE: Check edge coverage
    for idx, (u, v) in enumerate(edges):
        anc = ancilla_qubits[idx]
        # Compute: anc = 1 iff edge (u,v) is NOT covered
        # i.e., anc = (NOT p[u]) AND (NOT p[v])
        qc.x(problem_qubits[u])
        qc.x(problem_qubits[v])
        qc.ccx(problem_qubits[u], problem_qubits[v], anc)
        qc.x(problem_qubits[v])
        qc.x(problem_qubits[u])
    
    # Compute popcount using cascading additions
    count_bits = ancilla_qubits[8:11]
    
    # Sum problem_qubits into count_bits (3 bits for values 0-6)
    # Use ripple-adder-style logic
    carry = ancilla_qubits[8]
    sum_bit = ancilla_qubits[9]
    
    # Add first qubit: count = p[0]
    qc.cx(problem_qubits[0], sum_bit)
    
    # Add remaining qubits using full adder logic
    for i in range(1, 6):
        # Full adder: add p[i] to (carry, sum_bit)
        qc.ccx(sum_bit, problem_qubits[i], carry)
        qc.cx(problem_qubits[i], sum_bit)
    
    # Check popcount > 4: true if sum >= 5
    # sum >= 5 means (carry=1 AND sum_bit>=1) or (carry>=1)
    # Simplified: flag = carry (since max sum with carry=1 is 5-6)
    popcount_bad = ancilla_qubits[10]
    qc.cx(carry, popcount_bad)
    
    # Edge coverage: if any edge_ancilla is 1, it's bad
    all_edges_ok = ancilla_qubits[11]
    for i in range(8):
        qc.cx(ancilla_qubits[i], all_edges_ok)
    
    # all_edges_ok now holds parity; flip so 1 means all covered (all were 0)
    qc.x(all_edges_ok)
    
    # Apply phase only if valid (all edges covered AND popcount <= 4)
    # Validity = all_edges_ok AND (NOT popcount_bad)
    # Use AND: multiply conditions
    validity = ancilla_qubits[11]
    qc.cx(popcount_bad, validity)  # AND with NOT popcount_bad
    
    # Apply Z gate only if validity is 1
    qc.z(validity)
    
    # UNCOMPUTE: reverse all operations
    qc.cx(popcount_bad, validity)
    qc.x(all_edges_ok)
    for i in range(7, -1, -1):
        qc.cx(ancilla_qubits[i], all_edges_ok)
    
    qc.cx(carry, popcount_bad)
    for i in range(5, 0, -1):
        qc.cx(problem_qubits[i], sum_bit)
        qc.ccx(sum_bit, problem_qubits[i], carry)
    qc.cx(problem_qubits[0], sum_bit)
    
    for idx in range(7, -1, -1):
        u, v = edges[idx]
        anc = ancilla_qubits[idx]
        qc.x(problem_qubits[u])
        qc.x(problem_qubits[v])
        qc.ccx(problem_qubits[u], problem_qubits[v], anc)
        qc.x(problem_qubits[v])
        qc.x(problem_qubits[u])
