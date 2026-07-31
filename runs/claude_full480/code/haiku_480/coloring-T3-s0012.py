from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    """
    Grover oracle for 3-coloring a 5-vertex graph.
    Applies phase -1 to basis states where all edges connect different colors.
    
    Vertices 0-4, edges: (0,2), (0,4), (1,2), (1,4), (2,3), (2,4), (3,4)
    Each vertex v uses qubits [2v, 2v+1] as (low bit, high bit) encoding colors.
    Color decoding: 00→0, 01→1, 10→2, 11→0
    """
    
    edges = [(0, 2), (0, 4), (1, 2), (1, 4), (2, 3), (2, 4), (3, 4)]
    result = ancilla_qubits[3]
    
    # Initialize result to 1 (all constraints satisfied initially)
    qc.x(result)
    
    # For each edge, compute whether colors differ and AND into accumulator
    for u, v in edges:
        b0_u, b1_u = problem_qubits[2*u], problem_qubits[2*u+1]
        b0_v, b1_v = problem_qubits[2*v], problem_qubits[2*v+1]
        temp0, temp1, temp2 = ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[2]
        
        # Compute colors_differ into temp0
        # Colors are the same if:
        #   (b0_u ⊕ b1_u = 0) ∧ (b0_v ⊕ b1_v = 0)  [both color 0]
        #   ∨ (¬b0_u ∧ b1_u ∧ ¬b0_v ∧ b1_v)          [both color 2]
        #   ∨ (b0_u ∧ ¬b1_u ∧ b0_v ∧ ¬b1_v)          [both color 1]
        # colors_differ = NOT(colors_same)
        
        # Compute (b0_u ⊕ b1_u) into temp1
        qc.cx(b0_u, temp1)
        qc.cx(b1_u, temp1)
        
        # Compute (b0_v ⊕ b1_v) into temp2
        qc.cx(b0_v, temp2)
        qc.cx(b1_v, temp2)
        
        # Compute both_color_0 = NOT(temp1) ∧ NOT(temp2) into temp0
        qc.x(temp1)
        qc.x(temp2)
        qc.ccx(temp1, temp2, temp0)
        qc.x(temp2)
        qc.x(temp1)
        
        # Uncompute XORs
        qc.cx(b1_v, temp2)
        qc.cx(b0_v, temp2)
        qc.cx(b1_u, temp1)
        qc.cx(b0_u, temp1)
        
        # Compute both_color_2: (¬b0_u ∧ b1_u ∧ ¬b0_v ∧ b1_v)
        # temp1 = (¬b0_u ∧ b1_u)
        qc.x(b0_u)
        qc.ccx(b0_u, b1_u, temp1)
        qc.x(b0_u)
        
        # temp2 = (¬b0_v ∧ b1_v)
        qc.x(b0_v)
        qc.ccx(b0_v, b1_v, temp2)
        qc.x(b0_v)
        
        # OR temp0 with (temp1 ∧ temp2): temp0 = temp0 ∨ (temp1 ∧ temp2)
        # Use: NOT temp0 ∧ temp1 ∧ temp2, then flip temp0
        # This requires: qc.x(temp0); qc.mcx([temp0, temp1, temp2], result, mode='noancilla')
        # Simplified: if result=0, temp1=1, temp2=1 then set result=1
        # Use controlled approach: if temp1 & temp2, flip temp0
        qc.ccx(temp1, temp2, temp0)  # temp0 = temp0 XOR (temp1 ∧ temp2)
        
        # Reset temps
        qc.x(b0_v)
        qc.ccx(b0_v, b1_v, temp2)
        qc.x(b0_v)
        qc.x(b0_u)
        qc.ccx(b0_u, b1_u, temp1)
        qc.x(b0_u)
        
        # Compute both_color_1: (b0_u ∧ ¬b1_u ∧ b0_v ∧ ¬b1_v)
        # temp1 = (b0_u ∧ ¬b1_u)
        qc.x(b1_u)
        qc.ccx(b0_u, b1_u, temp1)
        qc.x(b1_u)
        
        # temp2 = (b0_v ∧ ¬b1_v)
        qc.x(b1_v)
        qc.ccx(b0_v, b1_v, temp2)
        qc.x(b1_v)
        
        # OR temp0 with (temp1 ∧ temp2)
        qc.ccx(temp1, temp2, temp0)
        
        # Reset temps
        qc.x(b1_v)
        qc.ccx(b0_v, b1_v, temp2)
        qc.x(b1_v)
        qc.x(b1_u)
        qc.ccx(b0_u, b1_u, temp1)
        qc.x(b1_u)
        
        # Now temp0 = colors_same; negate to get colors_differ
        qc.x(temp0)
        
        # AND result with colors_differ (temp0)
        qc.x(temp0)
        qc.cx(temp0, result)
        qc.x(temp0)
        
        # Reset temp0
        qc.x(temp0)
    
    # Apply phase flip
    qc.z(result)
    
    # Uncompute (reverse order)
    for u, v in reversed(edges):
        b0_u, b1_u = problem_qubits[2*u], problem_qubits[2*u+1]
        b0_v, b1_v = problem_qubits[2*v], problem_qubits[2*v+1]
        temp0, temp1, temp2 = ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[2]
        
        # Mirror of compute: start from colors_differ negated
        qc.x(temp0)
        qc.x(temp0)
        qc.cx(temp0, result)
        qc.x(temp0)
        qc.x(temp0)
        
        # Undo both_color_1
        qc.x(b1_u)
        qc.ccx(b0_u, b1_u, temp1)
        qc.x(b1_u)
        qc.x(b1_v)
        qc.ccx(b0_v, b1_v, temp2)
        qc.x(b1_v)
        qc.ccx(temp1, temp2, temp0)
        
        # Undo both_color_2
        qc.x(b0_u)
        qc.ccx(b0_u, b1_u, temp1)
        qc.x(b0_u)
        qc.x(b0_v)
        qc.ccx(b0_v, b1_v, temp2)
        qc.x(b0_v)
        qc.ccx(temp1, temp2, temp0)
        
        # Undo both_color_0
        qc.cx(b0_u, temp1)
        qc.cx(b1_u, temp1)
        qc.cx(b0_v, temp2)
        qc.cx(b1_v, temp2)
        qc.x(temp1)
        qc.x(temp2)
        qc.ccx(temp1, temp2, temp0)
        qc.x(temp2)
        qc.x(temp1)
        qc.cx(b1_v, temp2)
        qc.cx(b0_v, temp2)
        qc.cx(b1_u, temp1)
        qc.cx(b0_u, temp1)
    
    # Reset accumulator to |0>
    qc.x(result)
