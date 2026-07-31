from qiskit import QuantumCircuit
from qiskit.circuit.library import ZGate

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    """
    Grover oracle for graph coloring (5 vertices, 4 edges).
    Applies phase -1 to states where all edges connect vertices of different colors.
    
    Each vertex v uses 2 qubits: problem_qubits[2v] (low bit b0) and problem_qubits[2v+1] (high bit b1).
    Code c = b0 + 2*b1 maps to color: 0→0, 1→1, 2→2, 3→0 (surjective).
    """
    edges = [(0, 2), (0, 3), (0, 4), (1, 4)]
    
    # Compute same_color for each edge into ancilla[0:4]
    # same_color = 1 iff the two vertices have the same color
    for edge_idx, (u, v) in enumerate(edges):
        u_b0, u_b1 = problem_qubits[2*u], problem_qubits[2*u+1]
        v_b0, v_b1 = problem_qubits[2*v], problem_qubits[2*v+1]
        result = ancilla_qubits[edge_idx]
        
        # Check all 6 cases where colors match:
        # (u=00,v=00), (u=00,v=11), (u=01,v=01), (u=10,v=10), (u=11,v=00), (u=11,v=11)
        
        # Case 1: both 00 → ¬u_b0 ∧ ¬u_b1 ∧ ¬v_b0 ∧ ¬v_b1
        qc.x(u_b0)
        qc.x(u_b1)
        qc.x(v_b0)
        qc.x(v_b1)
        qc.mcx([u_b0, u_b1, v_b0, v_b1], result)
        qc.x(u_b0)
        qc.x(u_b1)
        qc.x(v_b0)
        qc.x(v_b1)
        
        # Case 2: u=00, v=11 → ¬u_b0 ∧ ¬u_b1 ∧ v_b0 ∧ v_b1
        qc.x(u_b0)
        qc.x(u_b1)
        qc.mcx([u_b0, u_b1, v_b0, v_b1], result)
        qc.x(u_b0)
        qc.x(u_b1)
        
        # Case 3: both 01 → u_b0 ∧ ¬u_b1 ∧ v_b0 ∧ ¬v_b1
        qc.x(u_b1)
        qc.x(v_b1)
        qc.mcx([u_b0, u_b1, v_b0, v_b1], result)
        qc.x(u_b1)
        qc.x(v_b1)
        
        # Case 4: both 10 → ¬u_b0 ∧ u_b1 ∧ ¬v_b0 ∧ v_b1
        qc.x(u_b0)
        qc.x(v_b0)
        qc.mcx([u_b0, u_b1, v_b0, v_b1], result)
        qc.x(u_b0)
        qc.x(v_b0)
        
        # Case 5: u=11, v=00 → u_b0 ∧ u_b1 ∧ ¬v_b0 ∧ ¬v_b1
        qc.x(v_b0)
        qc.x(v_b1)
        qc.mcx([u_b0, u_b1, v_b0, v_b1], result)
        qc.x(v_b0)
        qc.x(v_b1)
        
        # Case 6: both 11 → u_b0 ∧ u_b1 ∧ v_b0 ∧ v_b1
        qc.mcx([u_b0, u_b1, v_b0, v_b1], result)
    
    # ancilla[0:4] now contain same_color flags; set to 1 iff that edge is monochromatic
    # Apply Z phase iff all ancillas are 0 (i.e., all edges have different colors)
    # Use X-gates to flip controls, multi-controlled Z, then flip back
    for i in range(4):
        qc.x(ancilla_qubits[i])
    qc.mcp(ZGate(), ancilla_qubits[0:4], None)
    for i in range(4):
        qc.x(ancilla_qubits[i])
    
    # Uncompute: reverse computation to restore ancillas to |0⟩
    for edge_idx in range(len(edges) - 1, -1, -1):
        u, v = edges[edge_idx]
        u_b0, u_b1 = problem_qubits[2*u], problem_qubits[2*u+1]
        v_b0, v_b1 = problem_qubits[2*v], problem_qubits[2*v+1]
        result = ancilla_qubits[edge_idx]
        
        # Reverse all 6 cases in reverse order
        qc.mcx([u_b0, u_b1, v_b0, v_b1], result)
        
        qc.x(v_b0)
        qc.x(v_b1)
        qc.mcx([u_b0, u_b1, v_b0, v_b1], result)
        qc.x(v_b0)
        qc.x(v_b1)
        
        qc.x(u_b0)
        qc.x(v_b0)
        qc.mcx([u_b0, u_b1, v_b0, v_b1], result)
        qc.x(u_b0)
        qc.x(v_b0)
        
        qc.x(u_b1)
        qc.x(v_b1)
        qc.mcx([u_b0, u_b1, v_b0, v_b1], result)
        qc.x(u_b1)
        qc.x(v_b1)
        
        qc.x(u_b0)
        qc.x(u_b1)
        qc.mcx([u_b0, u_b1, v_b0, v_b1], result)
        qc.x(u_b0)
        qc.x(u_b1)
        
        qc.x(u_b0)
        qc.x(u_b1)
        qc.x(v_b0)
        qc.x(v_b1)
        qc.mcx([u_b0, u_b1, v_b0, v_b1], result)
        qc.x(u_b0)
        qc.x(u_b1)
        qc.x(v_b0)
        qc.x(v_b1)
