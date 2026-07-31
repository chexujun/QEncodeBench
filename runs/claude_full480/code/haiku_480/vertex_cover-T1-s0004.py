def build_oracle(qc, problem_qubits, ancilla_qubits):
    a0 = ancilla_qubits[0]  # for {1,2}
    a1 = ancilla_qubits[1]  # for {2,3}
    a2 = ancilla_qubits[2]  # for OR result
    
    # Compute: Check if state is {1,2} (x0=0, x1=1, x2=1, x3=0)
    qc.x(problem_qubits[0])
    qc.x(problem_qubits[3])
    qc.mcx([problem_qubits[0], problem_qubits[1], problem_qubits[2], problem_qubits[3]], a0)
    qc.x(problem_qubits[3])
    qc.x(problem_qubits[0])
    
    # Compute: Check if state is {2,3} (x0=0, x1=0, x2=1, x3=1)
    qc.x(problem_qubits[0])
    qc.x(problem_qubits[1])
    qc.mcx([problem_qubits[0], problem_qubits[1], problem_qubits[2], problem_qubits[3]], a1)
    qc.x(problem_qubits[1])
    qc.x(problem_qubits[0])
    
    # Compute: OR the two conditions
    qc.cx(a0, a2)
    qc.cx(a1, a2)
    
    # Phase: Apply Z to mark the marked states
    qc.z(a2)
    
    # Uncompute: Reverse the OR
    qc.cx(a1, a2)
    qc.cx(a0, a2)
    
    # Uncompute: Reverse the {2,3} check
    qc.x(problem_qubits[0])
    qc.x(problem_qubits[1])
    qc.mcx([problem_qubits[0], problem_qubits[1], problem_qubits[2], problem_qubits[3]], a1)
    qc.x(problem_qubits[1])
    qc.x(problem_qubits[0])
    
    # Uncompute: Reverse the {1,2} check
    qc.x(problem_qubits[0])
    qc.x(problem_qubits[3])
    qc.mcx([problem_qubits[0], problem_qubits[1], problem_qubits[2], problem_qubits[3]], a0)
    qc.x(problem_qubits[3])
    qc.x(problem_qubits[0])
