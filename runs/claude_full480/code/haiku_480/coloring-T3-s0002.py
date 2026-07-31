from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0,2), (0,5), (1,2), (1,3), (2,3), (3,4), (3,5)]
    
    # Ancilla allocation
    result = ancilla_qubits[0]   # Accumulator for constraint
    same_c = ancilla_qubits[1]   # Temporary for same_color computation
    temp1 = ancilla_qubits[2]    # Temporary for multi-controlled gates
    temp2 = ancilla_qubits[3]    # Temporary for multi-controlled gates
    
    # Initialize result to 1 (assume valid unless proven invalid)
    qc.x(result)
    
    # Forward pass: compute AND of all (NOT same_color) predicates
    for u, v in edges:
        u_b0 = problem_qubits[2*u]
        u_b1 = problem_qubits[2*u+1]
        v_b0 = problem_qubits[2*v]
        v_b1 = problem_qubits[2*v+1]
        
        # Compute same_color into same_c
        compute_same_color(qc, u_b0, u_b1, v_b0, v_b1, same_c, temp1, temp2)
        
        # Flip to get NOT same_color
        qc.x(same_c)
        
        # result = result AND same_c (where same_c is now NOT same_color)
        # Implementation: if same_c=0, result becomes 0; if same_c=1, result stays same
        # Using Toffoli: temp1 = result AND same_c
        qc.ccx(result, same_c, temp1)
        # Copy result back from temp1 by resetting result and XORing temp1
        qc.x(result)  # Flip result
        qc.cx(temp1, result)  # result = (NOT result) XOR temp1
        qc.x(result)  # Flip result back
        
        # Uncompute same_color
        qc.x(same_c)  # Flip back (undo the X)
        uncompute_same_color(qc, u_b0, u_b1, v_b0, v_b1, same_c, temp1, temp2)
    
    # Apply Z gate to result qubit (applies -1 phase when result=1, i.e., constraint satisfied)
    qc.z(result)
    
    # Backward pass: uncompute result back to 0
    for u, v in reversed(edges):
        u_b0 = problem_qubits[2*u]
        u_b1 = problem_qubits[2*u+1]
        v_b0 = problem_qubits[2*v]
        v_b1 = problem_qubits[2*v+1]
        
        # Recompute same_color into same_c
        compute_same_color(qc, u_b0, u_b1, v_b0, v_b1, same_c, temp1, temp2)
        
        # Flip to get NOT same_color
        qc.x(same_c)
        
        # Undo result = result AND same_c
        qc.x(result)
        qc.cx(temp1, result)
        qc.x(result)
        qc.ccx(result, same_c, temp1)
        
        # Uncompute same_color
        qc.x(same_c)
        uncompute_same_color(qc, u_b0, u_b1, v_b0, v_b1, same_c, temp1, temp2)


def compute_same_color(qc, u_b0, u_b1, v_b0, v_b1, result, temp1, temp2):
    """Compute result = 1 iff (u_b0,u_b1) and (v_b0,v_b1) decode to same color."""
    
    # Color mapping: 00→0, 01→1, 10→2, 11→0
    # Same color when: both 00, both 01, both 10, both 11, or one 00 and other 11
    
    # Condition 1: both 00
    qc.x(u_b0)
    qc.x(u_b1)
    qc.x(v_b0)
    qc.x(v_b1)
    qc.mcx([u_b0, u_b1, v_b0, v_b1], result, mode='dirty')
    qc.x(u_b0)
    qc.x(u_b1)
    qc.x(v_b0)
    qc.x(v_b1)
    
    # Condition 2: both 01
    qc.x(u_b0)
    qc.x(v_b0)
    qc.mcx([u_b0, u_b1, v_b0, v_b1], result, mode='dirty')
    qc.x(u_b0)
    qc.x(v_b0)
    
    # Condition 3: both 10
    qc.x(u_b1)
    qc.x(v_b1)
    qc.mcx([u_b0, u_b1, v_b0, v_b1], result, mode='dirty')
    qc.x(u_b1)
    qc.x(v_b1)
    
    # Condition 4: both 11
    qc.mcx([u_b0, u_b1, v_b0, v_b1], result, mode='dirty')
    
    # Condition 5: u=00, v=11
    qc.x(u_b0)
    qc.x(u_b1)
    qc.mcx([u_b0, u_b1, v_b0, v_b1], result, mode='dirty')
    qc.x(u_b0)
    qc.x(u_b1)
    
    # Condition 6: u=11, v=00
    qc.x(v_b0)
    qc.x(v_b1)
    qc.mcx([u_b0, u_b1, v_b0, v_b1], result, mode='dirty')
    qc.x(v_b0)
    qc.x(v_b1)


def uncompute_same_color(qc, u_b0, u_b1, v_b0, v_b1, result, temp1, temp2):
    """Uncompute same_color by applying it again (MCX is self-inverse)."""
    compute_same_color(qc, u_b0, u_b1, v_b0, v_b1, result, temp1, temp2)
