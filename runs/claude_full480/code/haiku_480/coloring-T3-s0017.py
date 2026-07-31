from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    """
    Graph 3-coloring oracle: marks states where all edges connect different-colored vertices.
    
    Color encoding: vertex v uses qubits problem_qubits[2v] (low) and problem_qubits[2v+1] (high).
    2-bit code to color: 00→0, 01→1, 10→2, 11→0.
    
    Two codes have the same color iff:
    - They are identical, OR
    - One is 00 and the other is 11 (both encode color 0)
    """
    edges = [(0,1), (0,2), (0,4), (1,4), (2,3), (2,4), (3,4)]
    
    # Ancilla qubits: track overall constraint satisfaction
    all_satisfied = ancilla_qubits[0]
    xor_b0 = ancilla_qubits[1]
    xor_b1 = ancilla_qubits[2]
    scratch = ancilla_qubits[3]
    
    # Initialize flag to |1> (all constraints satisfied initially)
    qc.x(all_satisfied)
    
    # FORWARD: compute constraints and apply phase
    for u, v in edges:
        b0_u = problem_qubits[2 * u]
        b1_u = problem_qubits[2 * u + 1]
        b0_v = problem_qubits[2 * v]
        b1_v = problem_qubits[2 * v + 1]
        
        # Compute b0_u XOR b0_v into xor_b0
        qc.cx(b0_u, xor_b0)
        qc.cx(b0_v, xor_b0)
        
        # Compute b1_u XOR b1_v into xor_b1
        qc.cx(b1_u, xor_b1)
        qc.cx(b1_v, xor_b1)
        
        # Case 1: codes are identical (both XORs are 0)
        # Compute into scratch if codes are identical
        qc.x(xor_b0)
        qc.x(xor_b1)
        qc.ccx(xor_b0, xor_b1, scratch)
        qc.x(xor_b0)
        qc.x(xor_b1)
        # scratch = 1 iff codes are identical
        
        # Case 2: products are identical (00 vs 11 case)
        # Compute (b0_u AND b1_u) XOR (b0_v AND b1_v)
        qc.ccx(b0_u, b1_u, xor_b0)
        qc.ccx(b0_v, b1_v, xor_b0)
        # xor_b0 = (b0_u AND b1_u) XOR (b0_v AND b1_v)
        # If this is 0, products are same (00 vs 11)
        
        # same_color = scratch OR (NOT xor_b0)
        # Compute using: result = NOT(NOT a AND NOT b) = a OR b
        qc.x(xor_b0)
        qc.x(scratch)
        qc.ccx(xor_b0, scratch, xor_b1)
        qc.x(xor_b0)
        qc.x(scratch)
        # xor_b1 = NOT((NOT xor_b0) AND (NOT scratch)) = same_color
        
        # If colors are same (constraint violated), flip all_satisfied
        qc.cx(xor_b1, all_satisfied)
        
        # Reset ancillas for next iteration
        qc.cx(b0_u, xor_b0)
        qc.cx(b0_v, xor_b0)
        qc.ccx(b0_u, b1_u, xor_b0)
        qc.ccx(b0_v, b1_v, xor_b0)
        qc.x(xor_b1)
        qc.x(scratch)
    
    # Apply phase -1 if all constraints are satisfied (all_satisfied = 1)
    qc.z(all_satisfied)
    
    # UNCOMPUTE: reverse operations to restore ancillas to |0>
    for u, v in reversed(edges):
        b0_u = problem_qubits[2 * u]
        b1_u = problem_qubits[2 * u + 1]
        b0_v = problem_qubits[2 * v]
        b1_v = problem_qubits[2 * v + 1]
        
        qc.x(xor_b1)
        qc.x(scratch)
        qc.cx(b0_u, xor_b0)
        qc.cx(b0_v, xor_b0)
        qc.ccx(b0_u, b1_u, xor_b0)
        qc.ccx(b0_v, b1_v, xor_b0)
        
        qc.cx(xor_b1, all_satisfied)
        
        qc.x(xor_b0)
        qc.x(scratch)
        qc.ccx(xor_b0, scratch, xor_b1)
        qc.x(xor_b0)
        qc.x(scratch)
        
        qc.ccx(b0_u, b1_u, xor_b0)
        qc.ccx(b0_v, b1_v, xor_b0)
        
        qc.x(xor_b0)
        qc.x(xor_b1)
        qc.ccx(xor_b0, xor_b1, scratch)
        qc.x(xor_b0)
        qc.x(xor_b1)
        
        qc.cx(b0_u, xor_b0)
        qc.cx(b0_v, xor_b0)
        qc.cx(b1_u, xor_b1)
        qc.cx(b1_v, xor_b1)
    
    # Restore all_satisfied to |0>
    qc.x(all_satisfied)
