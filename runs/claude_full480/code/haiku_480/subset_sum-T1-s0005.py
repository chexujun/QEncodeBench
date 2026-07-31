def build_oracle(qc, problem_qubits, ancilla_qubits):
    x0, x1, x2 = problem_qubits[0], problem_qubits[1], problem_qubits[2]
    work = ancilla_qubits[0]
    phase_qubit = ancilla_qubits[1]
    
    # Mark state |100> (only third element selected)
    # This is the only state where subset sum equals 5
    # Compute: NOT x0 AND NOT x1 AND x2
    
    # Flip x0 and x1 to represent NOT x0 and NOT x1
    qc.x(x0)
    qc.x(x1)
    
    # Compute AND of three qubits
    qc.ccx(x0, x1, work)           # work = (NOT x0) AND (NOT x1)
    qc.ccx(work, x2, phase_qubit)  # phase_qubit = work AND x2
    
    # Apply phase flip
    qc.z(phase_qubit)
    
    # Uncompute
    qc.ccx(work, x2, phase_qubit)
    qc.ccx(x0, x1, work)
    
    # Restore x0 and x1 to original values
    qc.x(x1)
    qc.x(x0)
