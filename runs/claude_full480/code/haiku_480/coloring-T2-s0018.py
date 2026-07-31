def build_oracle(qc, problem_qubits, ancilla_qubits):
    """
    Oracle for 3-coloring a 4-vertex graph with edges: (0,1), (0,2), (0,3), (1,2), (1,3).
    
    Each vertex v uses 2 qubits at indices 2*v and 2*v+1 to encode a color.
    Color encoding: c = b0 + 2*b1, where b0 = qubits[2*v], b1 = qubits[2*v+1].
    Decoding: 0,1,2 map to colors 0,1,2; 3 (binary 11) also maps to color 0.
    
    The oracle marks states where all edges connect vertices of different colors.
    """
    from qiskit.circuit.library import MCXGate
    
    edges = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3)]
    
    result_qubit = ancilla_qubits[0]
    constraint_qubits = [ancilla_qubits[i+1] for i in range(5)]
    
    # Initialize result to |1>
    qc.x(result_qubit)
    
    # Compute: each constraint[i] = 1 iff colors are SAME for edge i
    for i, (u, v) in enumerate(edges):
        b0_u = problem_qubits[2*u]
        b1_u = problem_qubits[2*u+1]
        b0_v = problem_qubits[2*v]
        b1_v = problem_qubits[2*v+1]
        target = constraint_qubits[i]
        
        # Compute constraint = 1 for same colors: (00,00), (00,11), (01,01), (10,10), (11,00), (11,11)
        
        # Case (00,00): all bits are 0
        qc.x(b0_u)
        qc.x(b1_u)
        qc.x(b0_v)
        qc.x(b1_v)
        qc.append(MCXGate(4), [b0_u, b1_u, b0_v, b1_v, target])
        qc.x(b0_u)
        qc.x(b1_u)
        qc.x(b0_v)
        qc.x(b1_v)
        
        # Case (00,11): b0_u=0, b1_u=0, b0_v=1, b1_v=1
        qc.x(b0_u)
        qc.x(b1_u)
        qc.append(MCXGate(4), [b0_u, b1_u, b0_v, b1_v, target])
        qc.x(b0_u)
        qc.x(b1_u)
        
        # Case (01,01): b0_u=1, b1_u=0, b0_v=1, b1_v=0
        qc.x(b1_u)
        qc.x(b1_v)
        qc.append(MCXGate(4), [b0_u, b1_u, b0_v, b1_v, target])
        qc.x(b1_u)
        qc.x(b1_v)
        
        # Case (10,10): b0_u=0, b1_u=1, b0_v=0, b1_v=1
        qc.x(b0_u)
        qc.x(b0_v)
        qc.append(MCXGate(4), [b0_u, b1_u, b0_v, b1_v, target])
        qc.x(b0_u)
        qc.x(b0_v)
        
        # Case (11,00): b0_u=1, b1_u=1, b0_v=0, b1_v=0
        qc.x(b0_v)
        qc.x(b1_v)
        qc.append(MCXGate(4), [b0_u, b1_u, b0_v, b1_v, target])
        qc.x(b0_v)
        qc.x(b1_v)
        
        # Case (11,11): all bits are 1
        qc.append(MCXGate(4), [b0_u, b1_u, b0_v, b1_v, target])
    
    # AND with inverted constraints: result &= NOT constraint[i] for all i
    # This ensures result=1 only when all constraints are 0 (i.e., all colors are different)
    for i in range(5):
        qc.x(constraint_qubits[i])  # Flip to get "colors_different"
        qc.ccx(result_qubit, constraint_qubits[i], result_qubit)
        qc.x(constraint_qubits[i])  # Flip back for symmetry
    
    # Apply phase
    qc.z(result_qubit)
    
    # Uncompute: reverse AND operations
    for i in range(4, -1, -1):
        qc.x(constraint_qubits[i])
        qc.ccx(result_qubit, constraint_qubits[i], result_qubit)
        qc.x(constraint_qubits[i])
    
    # Uncompute constraints
    for i in range(4, -1, -1):
        u, v = edges[i]
        b0_u = problem_qubits[2*u]
        b1_u = problem_qubits[2*u+1]
        b0_v = problem_qubits[2*v]
        b1_v = problem_qubits[2*v+1]
        target = constraint_qubits[i]
        
        qc.append(MCXGate(4), [b0_u, b1_u, b0_v, b1_v, target])
        
        qc.x(b0_v)
        qc.x(b1_v)
        qc.append(MCXGate(4), [b0_u, b1_u, b0_v, b1_v, target])
        qc.x(b0_v)
        qc.x(b1_v)
        
        qc.x(b0_u)
        qc.x(b0_v)
        qc.append(MCXGate(4), [b0_u, b1_u, b0_v, b1_v, target])
        qc.x(b0_u)
        qc.x(b0_v)
        
        qc.x(b1_u)
        qc.x(b1_v)
        qc.append(MCXGate(4), [b0_u, b1_u, b0_v, b1_v, target])
        qc.x(b1_u)
        qc.x(b1_v)
        
        qc.x(b0_u)
        qc.x(b1_u)
        qc.append(MCXGate(4), [b0_u, b1_u, b0_v, b1_v, target])
        qc.x(b0_u)
        qc.x(b1_u)
        
        qc.x(b0_u)
        qc.x(b1_u)
        qc.x(b0_v)
        qc.x(b1_v)
        qc.append(MCXGate(4), [b0_u, b1_u, b0_v, b1_v, target])
        qc.x(b0_u)
        qc.x(b1_u)
        qc.x(b0_v)
        qc.x(b1_v)
    
    # Uncompute result initialization
    qc.x(result_qubit)
