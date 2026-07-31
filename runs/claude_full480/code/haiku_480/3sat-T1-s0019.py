from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x = problem_qubits
    a = ancilla_qubits
    
    # COMPUTE c1: (NOT x1 OR x2 OR x3) is FALSE iff x1=1 AND x2=0 AND x3=0
    qc.x(x[2])
    qc.x(x[3])
    qc.mcx([x[1], x[2], x[3]], a[0])
    qc.x(x[3])
    qc.x(x[2])
    qc.x(a[0])  # a[0] = c1
    
    # COMPUTE c2: (NOT x0 OR NOT x1 OR NOT x3) is FALSE iff x0=1 AND x1=1 AND x3=1
    qc.mcx([x[0], x[1], x[3]], a[1])
    qc.x(a[1])  # a[1] = c2
    
    # COMPUTE c3: (NOT x0 OR x1 OR NOT x2) is FALSE iff x0=1 AND x1=0 AND x2=1
    qc.x(x[1])
    qc.mcx([x[0], x[1], x[2]], a[2])
    qc.x(x[1])
    qc.x(a[2])  # a[2] = c3
    
    # COMPUTE c4: (NOT x1 OR x2 OR NOT x3) is FALSE iff x1=1 AND x2=0 AND x3=1
    qc.x(x[2])
    qc.mcx([x[1], x[2], x[3]], a[3])
    qc.x(x[2])
    qc.x(a[3])  # a[3] = c4
    
    # COMPUTE c5: (NOT x0 OR NOT x2 OR x3) is FALSE iff x0=1 AND x2=1 AND x3=0
    qc.x(x[3])
    qc.mcx([x[0], x[2], x[3]], a[4])
    qc.x(x[3])
    qc.x(a[4])  # a[4] = c5
    
    # AND all clauses into a[5]
    qc.mcx([a[0], a[1], a[2], a[3], a[4]], a[5])
    
    # Apply phase -1 when all clauses are satisfied
    qc.z(a[5])
    
    # UNCOMPUTE: reverse all steps
    qc.mcx([a[0], a[1], a[2], a[3], a[4]], a[5])
    
    qc.x(a[4])
    qc.x(x[3])
    qc.mcx([x[0], x[2], x[3]], a[4])
    qc.x(x[3])
    qc.x(a[4])
    
    qc.x(a[3])
    qc.x(x[2])
    qc.mcx([x[1], x[2], x[3]], a[3])
    qc.x(x[2])
    qc.x(a[3])
    
    qc.x(a[2])
    qc.x(x[1])
    qc.mcx([x[0], x[1], x[2]], a[2])
    qc.x(x[1])
    qc.x(a[2])
    
    qc.x(a[1])
    qc.mcx([x[0], x[1], x[3]], a[1])
    qc.x(a[1])
    
    qc.x(a[0])
    qc.x(x[2])
    qc.x(x[3])
    qc.mcx([x[1], x[2], x[3]], a[0])
    qc.x(x[3])
    qc.x(x[2])
    qc.x(a[0])
