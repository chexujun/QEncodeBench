def build_oracle(qc, problem_qubits, ancilla_qubits):
    """
    Phase oracle for subset sum: f(x) = 1 iff the sum of selected elements 
    from a = [5, 4, 3] equals T = 8.
    
    Only the basis state |101> satisfies f(x) = 1 (selecting 5 + 3 = 8),
    so only this state receives a phase of -1.
    """
    x0, x1, x2 = problem_qubits[0], problem_qubits[1], problem_qubits[2]
    flag = ancilla_qubits[0]
    extra_ancillas = ancilla_qubits[1:]
    
    # Compute flag = 1 iff (x0=1 AND x1=0 AND x2=1)
    qc.x(x1)  # Flip x1 to create NOT x1
    qc.mcx([x0, x1, x2], flag, ancilla_qubits=extra_ancillas)  # flag = x0 AND x1 AND x2
    qc.z(flag)  # Apply phase -1 if flag=1
    qc.mcx([x0, x1, x2], flag, ancilla_qubits=extra_ancillas)  # Uncompute: clear flag
    qc.x(x1)  # Uncompute: flip x1 back
