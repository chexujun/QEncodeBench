from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x = problem_qubits
    a = ancilla_qubits
    
    # Compute NOT satisfied conditions for each clause into a[0:6]
    
    # Clause 1: (NOT x0 OR x1 OR NOT x4) => NOT satisfied iff x0 AND NOT x1 AND x4
    qc.x(x[1])
    qc.mcx([x[0], x[1], x[4]], a[0])
    qc.x(x[1])
    
    # Clause 2: (NOT x0 OR x1 OR x2) => NOT satisfied iff x0 AND NOT x1 AND NOT x2
    qc.x(x[1])
    qc.x(x[2])
    qc.mcx([x[0], x[1], x[2]], a[1])
    qc.x(x[2])
    qc.x(x[1])
    
    # Clause 3: (x0 OR NOT x3 OR NOT x4) => NOT satisfied iff NOT x0 AND x3 AND x4
    qc.x(x[0])
    qc.mcx([x[0], x[3], x[4]], a[2])
    qc.x(x[0])
    
    # Clause 4: (x1 OR x2 OR x3) => NOT satisfied iff NOT x1 AND NOT x2 AND NOT x3
    qc.x(x[1])
    qc.x(x[2])
    qc.x(x[3])
    qc.mcx([x[1], x[2], x[3]], a[3])
    qc.x(x[3])
    qc.x(x[2])
    qc.x(x[1])
    
    # Clause 5: (NOT x0 OR NOT x2 OR NOT x4) => NOT satisfied iff x0 AND x2 AND x4
    qc.mcx([x[0], x[2], x[4]], a[4])
    
    # Clause 6: (NOT x0 OR NOT x2 OR x4) => NOT satisfied iff x0 AND x2 AND NOT x4
    qc.x(x[4])
    qc.mcx([x[0], x[2], x[4]], a[5])
    qc.x(x[4])
    
    # Compute AND of NOT satisfied flags: a[6] = AND(NOT a[0], ..., NOT a[5])
    # This gives a[6] = 1 iff all clauses are satisfied
    for i in range(6):
        qc.x(a[i])
    qc.mcx([a[0], a[1], a[2], a[3], a[4], a[5]], a[6])
    for i in range(6):
        qc.x(a[i])
    
    # Apply phase -1 when a[6] = 1 (all clauses satisfied)
    qc.z(a[6])
    
    # Uncompute: reverse all steps
    for i in range(6):
        qc.x(a[i])
    qc.mcx([a[0], a[1], a[2], a[3], a[4], a[5]], a[6])
    for i in range(6):
        qc.x(a[i])
    
    qc.x(x[4])
    qc.mcx([x[0], x[2], x[4]], a[5])
    qc.x(x[4])
    
    qc.mcx([x[0], x[2], x[4]], a[4])
    
    qc.x(x[1])
    qc.x(x[2])
    qc.x(x[3])
    qc.mcx([x[1], x[2], x[3]], a[3])
    qc.x(x[3])
    qc.x(x[2])
    qc.x(x[1])
    
    qc.x(x[0])
    qc.mcx([x[0], x[3], x[4]], a[2])
    qc.x(x[0])
    
    qc.x(x[1])
    qc.x(x[2])
    qc.mcx([x[0], x[1], x[2]], a[1])
    qc.x(x[2])
    qc.x(x[1])
    
    qc.x(x[1])
    qc.mcx([x[0], x[1], x[4]], a[0])
    qc.x(x[1])
