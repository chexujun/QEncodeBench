def build_oracle(qc, problem_qubits, ancilla_qubits):
    q0, q1, q2 = problem_qubits[0], problem_qubits[1], problem_qubits[2]
    a = ancilla_qubits[0]
    
    # Compute: detect states where exactly 2 of 3 bits are 1 (sum = 5*2 = 10)
    # Pattern 1: (1, 1, 0)
    qc.x(q2)
    qc.mcx([q0, q1, q2], a)
    qc.x(q2)
    
    # Pattern 2: (1, 0, 1)
    qc.x(q1)
    qc.mcx([q0, q1, q2], a)
    qc.x(q1)
    
    # Pattern 3: (0, 1, 1)
    qc.x(q0)
    qc.mcx([q0, q1, q2], a)
    qc.x(q0)
    
    # Phase: apply -1 if marked
    qc.z(a)
    
    # Uncompute: reverse computation to restore ancilla to |0>
    qc.x(q0)
    qc.mcx([q0, q1, q2], a)
    qc.x(q0)
    
    qc.x(q1)
    qc.mcx([q0, q1, q2], a)
    qc.x(q1)
    
    qc.x(q2)
    qc.mcx([q0, q1, q2], a)
    qc.x(q2)
