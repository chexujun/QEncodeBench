import numpy as np

def build_oracle(qc, problem_qubits, ancilla_qubits):
    edges = [(0, 2), (1, 2), (3, 4)]
    edge_ancillas = ancilla_qubits[:3]
    result_ancilla = ancilla_qubits[3]
    
    # Step 1: Compute edge predicates into ancillas
    # For edge (u,v): edge_ok = (b0_u XOR b0_v) XOR (b1_u XOR b1_v)
    for idx, (u, v) in enumerate(edges):
        a = edge_ancillas[idx]
        b0_u, b1_u = problem_qubits[2*u], problem_qubits[2*u+1]
        b0_v, b1_v = problem_qubits[2*v], problem_qubits[2*v+1]
        
        # Compute XOR of both bit pairs
        qc.cx(b0_u, a)
        qc.cx(b0_v, a)
        qc.cx(b1_u, a)
        qc.cx(b1_v, a)
    
    # Step 2: Prepare result_ancilla in |1> state
    qc.x(result_ancilla)
    
    # Step 3: Apply multi-controlled phase
    # Applies -1 phase (e^{iπ}) when all three edge predicates are 1
    qc.mcp(np.pi, edge_ancillas, result_ancilla)
    
    # Step 4: Uncompute result_ancilla back to |0>
    qc.x(result_ancilla)
    
    # Step 5: Uncompute edge predicates (reverse order of computation)
    for idx in range(len(edges) - 1, -1, -1):
        u, v = edges[idx]
        a = edge_ancillas[idx]
        b0_u, b1_u = problem_qubits[2*u], problem_qubits[2*u+1]
        b0_v, b1_v = problem_qubits[2*v], problem_qubits[2*v+1]
        
        # Reverse the XOR computations
        qc.cx(b1_v, a)
        qc.cx(b1_u, a)
        qc.cx(b0_v, a)
        qc.cx(b0_u, a)
