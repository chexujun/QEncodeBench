def build_oracle(qc, problem_qubits, ancilla_qubits):
    from qiskit import QuantumCircuit
    import numpy as np
    
    edges = [(0, 1), (0, 2), (0, 4), (1, 2), (1, 3), (1, 4)]
    
    # Each edge gets an ancilla to mark if it's monochromatic
    edge_ancs = ancilla_qubits[0:6]
    temp_anc = ancilla_qubits[6]
    
    # Compute monochromatic condition for each edge
    for edge_idx, (u, v) in enumerate(edges):
        c0_u = problem_qubits[2*u]
        c1_u = problem_qubits[2*u+1]
        c0_v = problem_qubits[2*v]
        c1_v = problem_qubits[2*v+1]
        edge_anc = edge_ancs[edge_idx]
        
        # Monochromatic patterns (same color for both vertices):
        # Color 0 (codes 00 or 11): (0,0,0,0), (0,0,1,1), (1,1,0,0), (1,1,1,1)
        # Color 1 (code 01): (1,0,1,0)
        # Color 2 (code 10): (0,1,0,1)
        qc.mcx([c0_u, c1_u, c0_v, c1_v], edge_anc, ctrl_state=0b0000)
        qc.mcx([c0_u, c1_u, c0_v, c1_v], edge_anc, ctrl_state=0b1100)
        qc.mcx([c0_u, c1_u, c0_v, c1_v], edge_anc, ctrl_state=0b0011)
        qc.mcx([c0_u, c1_u, c0_v, c1_v], edge_anc, ctrl_state=0b1111)
        qc.mcx([c0_u, c1_u, c0_v, c1_v], edge_anc, ctrl_state=0b1010)
        qc.mcx([c0_u, c1_u, c0_v, c1_v], edge_anc, ctrl_state=0b0101)
    
    # Invert edge_ancs so they're 1 iff edges are non-monochromatic
    for anc in edge_ancs:
        qc.x(anc)
    
    # Compute AND of all (inverted) edge_ancs into temp_anc
    qc.x(temp_anc)  # temp_anc = 1
    for anc in edge_ancs:
        qc.ccx(temp_anc, anc, temp_anc)  # temp_anc = temp_anc AND anc
    
    # temp_anc is now 1 iff all edges are non-monochromatic (valid coloring)
    # Apply Z gate to encode phase -1
    qc.z(temp_anc)
    
    # Uncompute temp_anc
    for anc in reversed(edge_ancs):
        qc.ccx(temp_anc, anc, temp_anc)
    qc.x(temp_anc)
    
    # Uncompute X-inversions of edge_ancs
    for anc in edge_ancs:
        qc.x(anc)
    
    # Uncompute monochromatic conditions (reverse order)
    for edge_idx, (u, v) in enumerate(edges):
        c0_u = problem_qubits[2*u]
        c1_u = problem_qubits[2*u+1]
        c0_v = problem_qubits[2*v]
        c1_v = problem_qubits[2*v+1]
        edge_anc = edge_ancs[edge_idx]
        
        qc.mcx([c0_u, c1_u, c0_v, c1_v], edge_anc, ctrl_state=0b0101)
        qc.mcx([c0_u, c1_u, c0_v, c1_v], edge_anc, ctrl_state=0b1010)
        qc.mcx([c0_u, c1_u, c0_v, c1_v], edge_anc, ctrl_state=0b1111)
        qc.mcx([c0_u, c1_u, c0_v, c1_v], edge_anc, ctrl_state=0b0011)
        qc.mcx([c0_u, c1_u, c0_v, c1_v], edge_anc, ctrl_state=0b1100)
        qc.mcx([c0_u, c1_u, c0_v, c1_v], edge_anc, ctrl_state=0b0000)
