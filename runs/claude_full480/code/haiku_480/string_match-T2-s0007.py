def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    q = problem_qubits
    a = ancilla_qubits
    
    # Compute a[0] = q[1] AND q[2] AND q[3] AND q[4]
    qc.mcx([q[1], q[2], q[3], q[4]], a[0])
    
    # Compute a[1] = q[2] AND q[3] AND q[4] AND q[5]
    qc.mcx([q[2], q[3], q[4], q[5]], a[1])
    
    # Compute a[2] = a[0] OR a[1] using NOT(NOT a[0] AND NOT a[1])
    qc.x(a[0])
    qc.x(a[1])
    qc.ccx(a[0], a[1], a[2])
    qc.x(a[2])
    
    # Apply phase
    qc.z(a[2])
    
    # Uncompute a[2]
    qc.x(a[2])
    qc.ccx(a[0], a[1], a[2])
    qc.x(a[1])
    qc.x(a[0])
    
    # Uncompute a[1]
    qc.mcx([q[2], q[3], q[4], q[5]], a[1])
    
    # Uncompute a[0]
    qc.mcx([q[1], q[2], q[3], q[4]], a[0])
