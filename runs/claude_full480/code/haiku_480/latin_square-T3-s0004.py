from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    q = problem_qubits
    a = ancilla_qubits
    
    # Constraint 1: (q0, q1) must make value 0, i.e., q0 = q1 (XNOR)
    # a[0] = q0 XOR q1 (should be 0 if satisfied)
    qc.cx(q[0], a[0])
    qc.cx(q[1], a[0])
    
    # Constraint 2a: q2 must be 1
    # a[1] = q2 XOR 1 (should be 0 if q2 = 1)
    qc.x(q[2])
    qc.cx(q[2], a[1])
    qc.x(q[2])
    
    # Constraint 2b: q3 must be 0
    # a[2] = q3 (should be 0 if q3 = 0)
    qc.cx(q[3], a[2])
    
    # Constraint 3a: q4 must be 0
    # a[3] = q4 (should be 0 if q4 = 0)
    qc.cx(q[4], a[3])
    
    # Constraint 3b: q5 must be 1
    # a[4] = q5 XOR 1 (should be 0 if q5 = 1)
    qc.x(q[5])
    qc.cx(q[5], a[4])
    qc.x(q[5])
    
    # Constraint 4: (q6, q7) must make value 0, i.e., q6 = q7 (XNOR)
    # a[5] = q6 XOR q7 (should be 0 if satisfied)
    qc.cx(q[6], a[5])
    qc.cx(q[7], a[5])
    
    # Flip all ancillas: a[i] := NOT(a[i])
    # After flip, a[i] = 1 iff constraint i is satisfied
    for i in range(6):
        qc.x(a[i])
    
    # Apply multi-controlled Z: apply phase -1 iff all a[i] = 1 (all constraints satisfied)
    # Use H-mcx-H decomposition for multi-controlled Z
    qc.h(a[0])
    qc.mcx([a[1], a[2], a[3], a[4], a[5]], a[0])
    qc.h(a[0])
    
    # Unflip all ancillas
    for i in range(6):
        qc.x(a[i])
    
    # Uncompute constraint 4
    qc.cx(q[7], a[5])
    qc.cx(q[6], a[5])
    
    # Uncompute constraint 3b
    qc.x(q[5])
    qc.cx(q[5], a[4])
    qc.x(q[5])
    
    # Uncompute constraint 3a
    qc.cx(q[4], a[3])
    
    # Uncompute constraint 2b
    qc.cx(q[3], a[2])
    
    # Uncompute constraint 2a
    qc.x(q[2])
    qc.cx(q[2], a[1])
    qc.x(q[2])
    
    # Uncompute constraint 1
    qc.cx(q[1], a[0])
    qc.cx(q[0], a[0])
