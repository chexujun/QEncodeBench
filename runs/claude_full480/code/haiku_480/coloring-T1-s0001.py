from qiskit import QuantumCircuit

def build_oracle(qc, problem_qubits, ancilla_qubits):
    edges = [(0, 1), (2, 3), (2, 4), (3, 4)]
    
    # Compute edge invalidity (same color) for each edge
    for idx, (u, v) in enumerate(edges):
        compute_edge_invalid(qc, problem_qubits, u, v, ancilla_qubits[idx])
    
    # Convert invalidity to validity by flipping
    for i in range(4):
        qc.x(ancilla_qubits[i])
    
    # Combine all validities: ancilla[4] = 1 iff all edges are valid
    qc.mcp(None, [ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[2], ancilla_qubits[3]], 
           ancilla_qubits[4], mode='v-chain')
    
    # Apply phase gate
    qc.z(ancilla_qubits[4])
    
    # Uncompute multi-controlled X
    qc.mcp(None, [ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[2], ancilla_qubits[3]], 
           ancilla_qubits[4], mode='v-chain')
    
    # Convert back to invalidity
    for i in range(4):
        qc.x(ancilla_qubits[i])
    
    # Uncompute edge invalidity (reverse order)
    for idx, (u, v) in enumerate(reversed(edges)):
        uncompute_edge_invalid(qc, problem_qubits, u, v, ancilla_qubits[len(edges) - 1 - idx])

def compute_edge_invalid(qc, problem_qubits, u, v, ancilla):
    b0_u = problem_qubits[2*u]
    b1_u = problem_qubits[2*u + 1]
    b0_v = problem_qubits[2*v]
    b1_v = problem_qubits[2*v + 1]
    
    # Edge invalid iff colors match: exactly one of 6 cases per 4-bit input
    # XOR all conditions (equivalent to OR since only one true per input)
    
    # Condition 1: (¬b0_u ∧ ¬b1_u ∧ ¬b0_v ∧ ¬b1_v) [code 00,00]
    qc.x(b0_u); qc.x(b1_u); qc.x(b0_v); qc.x(b1_v)
    qc.mcx([b0_u, b1_u, b0_v, b1_v], ancilla)
    qc.x(b0_u); qc.x(b1_u); qc.x(b0_v); qc.x(b1_v)
    
    # Condition 2: (¬b0_u ∧ ¬b1_u ∧ b0_v ∧ b1_v) [code 00,11]
    qc.x(b0_u); qc.x(b1_u)
    qc.mcx([b0_u, b1_u, b0_v, b1_v], ancilla)
    qc.x(b0_u); qc.x(b1_u)
    
    # Condition 3: (b0_u ∧ b1_u ∧ ¬b0_v ∧ ¬b1_v) [code 11,00]
    qc.x(b0_v); qc.x(b1_v)
    qc.mcx([b0_u, b1_u, b0_v, b1_v], ancilla)
    qc.x(b0_v); qc.x(b1_v)
    
    # Condition 4: (b0_u ∧ b1_u ∧ b0_v ∧ b1_v) [code 11,11]
    qc.mcx([b0_u, b1_u, b0_v, b1_v], ancilla)
    
    # Condition 5: (b0_u ∧ ¬b1_u ∧ b0_v ∧ ¬b1_v) [code 01,01]
    qc.x(b1_u); qc.x(b1_v)
    qc.mcx([b0_u, b1_u, b0_v, b1_v], ancilla)
    qc.x(b1_u); qc.x(b1_v)
    
    # Condition 6: (¬b0_u ∧ b1_u ∧ ¬b0_v ∧ b1_v) [code 10,10]
    qc.x(b0_u); qc.x(b0_v)
    qc.mcx([b0_u, b1_u, b0_v, b1_v], ancilla)
    qc.x(b0_u); qc.x(b0_v)

def uncompute_edge_invalid(qc, problem_qubits, u, v, ancilla):
    b0_u = problem_qubits[2*u]
    b1_u = problem_qubits[2*u + 1]
    b0_v = problem_qubits[2*v]
    b1_v = problem_qubits[2*v + 1]
    
    # Reverse order uncompute
    qc.x(b0_u); qc.x(b0_v)
    qc.mcx([b0_u, b1_u, b0_v, b1_v], ancilla)
    qc.x(b0_u); qc.x(b0_v)
    
    qc.x(b1_u); qc.x(b1_v)
    qc.mcx([b0_u, b1_u, b0_v, b1_v], ancilla)
    qc.x(b1_u); qc.x(b1_v)
    
    qc.mcx([b0_u, b1_u, b0_v, b1_v], ancilla)
    
    qc.x(b0_v); qc.x(b1_v)
    qc.mcx([b0_u, b1_u, b0_v, b1_v], ancilla)
    qc.x(b0_v); qc.x(b1_v)
    
    qc.x(b0_u); qc.x(b1_u)
    qc.mcx([b0_u, b1_u, b0_v, b1_v], ancilla)
    qc.x(b0_u); qc.x(b1_u)
    
    qc.x(b0_u); qc.x(b1_u); qc.x(b0_v); qc.x(b1_v)
    qc.mcx([b0_u, b1_u, b0_v, b1_v], ancilla)
    qc.x(b0_u); qc.x(b1_u); qc.x(b0_v); qc.x(b1_v)
