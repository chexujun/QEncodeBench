from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x = problem_qubits
    a = ancilla_qubits
    
    # Clause 1: (x0 OR x1 OR x2) is FALSE iff (NOT x0 AND NOT x1 AND NOT x2)
    qc.x(x[0])
    qc.x(x[1])
    qc.x(x[2])
    qc.mcx([x[0], x[1], x[2]], a[0])
    qc.x(x[0])
    qc.x(x[1])
    qc.x(x[2])
    
    # Clause 2: (NOT x0 OR NOT x1 OR NOT x2) is FALSE iff (x0 AND x1 AND x2)
    qc.mcx([x[0], x[1], x[2]], a[1])
    
    # Clause 3: (x0 OR x2 OR NOT x3) is FALSE iff (NOT x0 AND NOT x2 AND x3)
    qc.x(x[0])
    qc.x(x[2])
    qc.mcx([x[0], x[2], x[3]], a[2])
    qc.x(x[0])
    qc.x(x[2])
    
    # Clause 4: (x0 OR NOT x2 OR x4) is FALSE iff (NOT x0 AND x2 AND NOT x4)
    qc.x(x[0])
    qc.x(x[4])
    qc.mcx([x[0], x[2], x[4]], a[3])
    qc.x(x[0])
    qc.x(x[4])
    
    # Clause 5: (NOT x0 OR x1 OR NOT x3) is FALSE iff (x0 AND NOT x1 AND x3)
    qc.x(x[1])
    qc.mcx([x[0], x[1], x[3]], a[4])
    qc.x(x[1])
    
    # Combine: a[5] = 1 iff all clauses satisfied (all a[0..4] are 0)
    qc.x(a[0])
    qc.x(a[1])
    qc.x(a[2])
    qc.x(a[3])
    qc.x(a[4])
    qc.mcx([a[0], a[1], a[2], a[3], a[4]], a[5])
    qc.x(a[0])
    qc.x(a[1])
    qc.x(a[2])
    qc.x(a[3])
    qc.x(a[4])
    
    # Phase: apply Z to mark solutions
    qc.z(a[5])
    
    # Uncompute a[5]
    qc.x(a[0])
    qc.x(a[1])
    qc.x(a[2])
    qc.x(a[3])
    qc.x(a[4])
    qc.mcx([a[0], a[1], a[2], a[3], a[4]], a[5])
    qc.x(a[0])
    qc.x(a[1])
    qc.x(a[2])
    qc.x(a[3])
    qc.x(a[4])
    
    # Uncompute clause ancillas (reverse order)
    qc.x(x[1])
    qc.mcx([x[0], x[1], x[3]], a[4])
    qc.x(x[1])
    
    qc.x(x[0])
    qc.x(x[4])
    qc.mcx([x[0], x[2], x[4]], a[3])
    qc.x(x[0])
    qc.x(x[4])
    
    qc.x(x[0])
    qc.x(x[2])
    qc.mcx([x[0], x[2], x[3]], a[2])
    qc.x(x[0])
    qc.x(x[2])
    
    qc.mcx([x[0], x[1], x[2]], a[1])
    
    qc.x(x[0])
    qc.x(x[1])
    qc.x(x[2])
    qc.mcx([x[0], x[1], x[2]], a[0])
    qc.x(x[0])
    qc.x(x[1])
    qc.x(x[2])
