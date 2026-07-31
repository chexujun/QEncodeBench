def build_oracle(qc, problem_qubits, ancilla_qubits):
    """
    Oracle for graph coloring problem on 4-vertex graph.
    Applies phase -1 to basis states where all edges have endpoints
    of different colors (valid 3-colorings under surjective encoding).
    """
    # Vertex i has color bits at problem_qubits[2i] (low) and problem_qubits[2i+1] (high)
    v = [[problem_qubits[2*i], problem_qubits[2*i+1]] for i in range(4)]
    
    # Edges of the graph
    edges = [(0, 1), (0, 2), (1, 2), (1, 3), (2, 3)]
    
    a = list(ancilla_qubits)
    
    # COMPUTE: Edge validity flags into ancillas a[0:5]
    # For each edge (u, v), flag = (bu0 XOR bv0) XOR (bu1 XOR bv1)
    # This equals 1 iff the vertices have different colors
    # (because colors differ when Hamming distance in bits is odd)
    for i, (u, v_idx) in enumerate(edges):
        qc.cx(v[u][0], a[i])      # Accumulate low-bit difference
        qc.cx(v[v_idx][0], a[i])
        qc.cx(v[u][1], a[i])      # Accumulate high-bit difference
        qc.cx(v[v_idx][1], a[i])
    
    # COMPUTE: AND of all edge flags into ancilla a[5]
    # The multi-controlled-X gate: mcx flips a[5] iff all of a[0:5] are 1
    # Since a[5] starts at |0>, after mcx: a[5] = a[0] AND a[1] AND ... AND a[4]
    qc.mcx(a[0:5], a[5])
    
    # PHASE: Apply Z to marked state (where a[5] = 1, meaning all edges valid)
    # This multiplies the marked state's amplitude by -1
    qc.z(a[5])
    
    # UNCOMPUTE: Reverse the AND computation (mcx is self-inverse)
    qc.mcx(a[0:5], a[5])
    
    # UNCOMPUTE: Restore all edge flags by reversing the XOR operations
    for i, (u, v_idx) in enumerate(edges):
        qc.cx(v[v_idx][1], a[i])  # Reverse high-bit accumulation
        qc.cx(v[u][1], a[i])
        qc.cx(v[v_idx][0], a[i])  # Reverse low-bit accumulation
        qc.cx(v[u][0], a[i])
