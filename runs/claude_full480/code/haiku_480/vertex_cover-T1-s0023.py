def build_oracle(qc, problem_qubits, ancilla_qubits):
    x0, x1, x2, x3 = problem_qubits
    a = ancilla_qubits[0]
    
    # The graph K_{2,2} has edges (0,2), (0,3), (1,2), (1,3)
    # Valid vertex covers of size ≤ 2: {0,1} and {2,3}
    # These correspond to binary states (1,1,0,0) and (0,0,1,1)
    
    # Compute: a = 1 iff input is (1,1,0,0) or (0,0,1,1)
    qc.mcx([x0, x1, x2, x3], a, ctrl_state='1100')
    qc.mcx([x0, x1, x2, x3], a, ctrl_state='0011')
    
    # Apply phase -1
    qc.z(a)
    
    # Uncompute: return a to |0>
    qc.mcx([x0, x1, x2, x3], a, ctrl_state='0011')
    qc.mcx([x0, x1, x2, x3], a, ctrl_state='1100')
