from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x = problem_qubits
    a = ancilla_qubits
    
    # Compute clause 1: (NOT x2 OR x3 OR x5)
    # NOT satisfied when: x2 AND NOT x3 AND NOT x5
    qc.x(x[3])
    qc.x(x[5])
    qc.mcx([x[2], x[3], x[5]], a[0])
    qc.x(a[0])
    qc.x(x[5])
    qc.x(x[3])
    
    # Compute clause 2: (x2 OR x4 OR x5)
    # NOT satisfied when: NOT x2 AND NOT x4 AND NOT x5
    qc.x(x[2])
    qc.x(x[4])
    qc.x(x[5])
    qc.mcx([x[2], x[4], x[5]], a[1])
    qc.x(a[1])
    qc.x(x[5])
    qc.x(x[4])
    qc.x(x[2])
    
    # Compute clause 3: (NOT x1 OR x3 OR NOT x5)
    # NOT satisfied when: x1 AND NOT x3 AND x5
    qc.x(x[1])
    qc.x(x[5])
    qc.mcx([x[1], x[3], x[5]], a[2])
    qc.x(a[2])
    qc.x(x[5])
    qc.x(x[1])
    
    # Compute clause 4: (NOT x1 OR NOT x4 OR x5)
    # NOT satisfied when: x1 AND x4 AND NOT x5
    qc.x(x[1])
    qc.x(x[4])
    qc.mcx([x[1], x[4], x[5]], a[3])
    qc.x(a[3])
    qc.x(x[4])
    qc.x(x[1])
    
    # Compute clause 5: (x0 OR NOT x2 OR NOT x3)
    # NOT satisfied when: NOT x0 AND x2 AND x3
    qc.x(x[0])
    qc.x(x[2])
    qc.x(x[3])
    qc.mcx([x[0], x[2], x[3]], a[4])
    qc.x(a[4])
    qc.x(x[3])
    qc.x(x[2])
    qc.x(x[0])
    
    # Compute AND of all clauses into a[5] and apply phase
    qc.mcx([a[0], a[1], a[2], a[3], a[4]], a[5])
    qc.z(a[5])
    qc.mcx([a[0], a[1], a[2], a[3], a[4]], a[5])
    
    # Uncompute clause 5
    qc.x(x[0])
    qc.x(x[2])
    qc.x(x[3])
    qc.x(a[4])
    qc.mcx([x[0], x[2], x[3]], a[4])
    qc.x(x[3])
    qc.x(x[2])
    qc.x(x[0])
    
    # Uncompute clause 4
    qc.x(x[1])
    qc.x(x[4])
    qc.x(a[3])
    qc.mcx([x[1], x[4], x[5]], a[3])
    qc.x(x[4])
    qc.x(x[1])
    
    # Uncompute clause 3
    qc.x(x[1])
    qc.x(x[5])
    qc.x(a[2])
    qc.mcx([x[1], x[3], x[5]], a[2])
    qc.x(x[5])
    qc.x(x[1])
    
    # Uncompute clause 2
    qc.x(x[2])
    qc.x(x[4])
    qc.x(x[5])
    qc.x(a[1])
    qc.mcx([x[2], x[4], x[5]], a[1])
    qc.x(x[5])
    qc.x(x[4])
    qc.x(x[2])
    
    # Uncompute clause 1
    qc.x(x[3])
    qc.x(x[5])
    qc.x(a[0])
    qc.mcx([x[2], x[3], x[5]], a[0])
    qc.x(x[5])
    qc.x(x[3])
