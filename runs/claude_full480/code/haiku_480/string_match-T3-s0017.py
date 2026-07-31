def build_oracle(qc, problem_qubits, ancilla_qubits):
    offset_ancilla = ancilla_qubits[0]
    or_result = ancilla_qubits[1]
    temp = ancilla_qubits[2]
    
    offsets_to_check = [
        (1, 2, 3),
        (2, 3, 4),
        (3, 4, 5),
        (4, 5, 6),
        (5, 6, 7),
    ]
    
    # Forward pass: compute each offset match and accumulate OR
    for idx1, idx2, idx3 in offsets_to_check:
        qc.mcx([problem_qubits[idx1], problem_qubits[idx2], problem_qubits[idx3]], offset_ancilla)
        qc.x(or_result)
        qc.ccx(offset_ancilla, or_result, temp)
        qc.x(or_result)
        qc.cx(temp, or_result)
        qc.mcx([problem_qubits[idx1], problem_qubits[idx2], problem_qubits[idx3]], offset_ancilla)
    
    # Apply phase kick via Z gate
    qc.z(or_result)
    
    # Uncompute: reverse all operations
    for idx1, idx2, idx3 in reversed(offsets_to_check):
        qc.mcx([problem_qubits[idx1], problem_qubits[idx2], problem_qubits[idx3]], offset_ancilla)
        qc.cx(temp, or_result)
        qc.x(or_result)
        qc.ccx(offset_ancilla, or_result, temp)
        qc.x(or_result)
        qc.mcx([problem_qubits[idx1], problem_qubits[idx2], problem_qubits[idx3]], offset_ancilla)
