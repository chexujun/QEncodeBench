from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x = problem_qubits  # x[0..5]
    a = ancilla_qubits  # a[0..5]
    
    # Compute Clause 1: (x1 OR x2 OR x5)
    # False only when x1=0, x2=0, x5=0
    qc.x(x[1])
    qc.x(x[2])
    qc.x(x[5])
    qc.mcx([x[1], x[2], x[5]], a[0])
    qc.x(x[5])
    qc.x(x[2])
    qc.x(x[1])
    qc.x(a[0])
    
    # Compute Clause 2: (NOT x1 OR x2 OR NOT x4)
    # False only when x1=1, x2=0, x4=1
    qc.x(x[2])
    qc.mcx([x[1], x[2], x[4]], a[1])
    qc.x(x[2])
    qc.x(a[1])
    
    # Compute Clause 3: (NOT x0 OR NOT x1 OR NOT x3)
    # False only when x0=1, x1=1, x3=1
    qc.mcx([x[0], x[1], x[3]], a[2])
    qc.x(a[2])
    
    # Compute Clause 4: (x2 OR NOT x4 OR NOT x5)
    # False only when x2=0, x4=1, x5=1
    qc.x(x[2])
    qc.mcx([x[2], x[4], x[5]], a[3])
    qc.x(x[2])
    qc.x(a[3])
    
    # Compute Clause 5: (x1 OR x4 OR NOT x5)
    # False only when x1=0, x4=0, x5=1
    qc.x(x[1])
    qc.x(x[4])
    qc.mcx([x[1], x[4], x[5]], a[4])
    qc.x(x[4])
    qc.x(x[1])
    qc.x(a[4])
    
    # AND all clause flags into a[5]
    qc.mcx([a[0], a[1], a[2], a[3], a[4]], a[5])
    
    # Apply phase -1 when all clauses are satisfied
    qc.z(a[5])
    
    # Uncompute: reverse operations
    qc.mcx([a[0], a[1], a[2], a[3], a[4]], a[5])
    
    # Uncompute Clause 5
    qc.x(a[4])
    qc.x(x[1])
    qc.x(x[4])
    qc.mcx([x[1], x[4], x[5]], a[4])
    qc.x(x[4])
    qc.x(x[1])
    
    # Uncompute Clause 4
    qc.x(a[3])
    qc.x(x[2])
    qc.mcx([x[2], x[4], x[5]], a[3])
    qc.x(x[2])
    
    # Uncompute Clause 3
    qc.x(a[2])
    qc.mcx([x[0], x[1], x[3]], a[2])
    
    # Uncompute Clause 2
    qc.x(a[1])
    qc.x(x[2])
    qc.mcx([x[1], x[2], x[4]], a[1])
    qc.x(x[2])
    
    # Uncompute Clause 1
    qc.x(a[0])
    qc.x(x[1])
    qc.x(x[2])
    qc.x(x[5])
    qc.mcx([x[1], x[2], x[5]], a[0])
    qc.x(x[5])
    qc.x(x[2])
    qc.x(x[1])
