from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x = problem_qubits  # [x0, x1, x2, x3, x4]
    a = ancilla_qubits  # [a0, a1, a2, a3, a4]
    
    # Compute when each clause is FALSE into a[0:4]
    
    # Clause 1: (NOT x1 OR NOT x2 OR x3) is FALSE iff (x1=1 AND x2=1 AND x3=0)
    qc.x(x[3])
    qc.mcx([x[1], x[2], x[3]], a[0])
    qc.x(x[3])
    
    # Clause 2: (NOT x0 OR NOT x3 OR NOT x4) is FALSE iff (x0=1 AND x3=1 AND x4=1)
    qc.mcx([x[0], x[3], x[4]], a[1])
    
    # Clause 3: (x0 OR x1 OR x2) is FALSE iff (x0=0 AND x1=0 AND x2=0)
    qc.x(x[0])
    qc.x(x[1])
    qc.x(x[2])
    qc.mcx([x[0], x[1], x[2]], a[2])
    qc.x(x[0])
    qc.x(x[1])
    qc.x(x[2])
    
    # Clause 4: (NOT x1 OR x2 OR x4) is FALSE iff (x1=1 AND x2=0 AND x4=0)
    qc.x(x[2])
    qc.x(x[4])
    qc.mcx([x[1], x[2], x[4]], a[3])
    qc.x(x[2])
    qc.x(x[4])
    
    # Now a[0:4] are 1 iff the corresponding clause is FALSE
    # Flip to indicate "clause is TRUE"
    qc.x(a[0])
    qc.x(a[1])
    qc.x(a[2])
    qc.x(a[3])
    
    # Compute AND into a[4]: a[4] = 1 iff all clauses are TRUE
    qc.mcx([a[0], a[1], a[2], a[3]], a[4])
    
    # Apply phase
    qc.z(a[4])
    
    # Uncompute AND
    qc.mcx([a[0], a[1], a[2], a[3]], a[4])
    
    # Flip back
    qc.x(a[0])
    qc.x(a[1])
    qc.x(a[2])
    qc.x(a[3])
    
    # Uncompute clause 4
    qc.x(x[2])
    qc.x(x[4])
    qc.mcx([x[1], x[2], x[4]], a[3])
    qc.x(x[2])
    qc.x(x[4])
    
    # Uncompute clause 3
    qc.x(x[0])
    qc.x(x[1])
    qc.x(x[2])
    qc.mcx([x[0], x[1], x[2]], a[2])
    qc.x(x[0])
    qc.x(x[1])
    qc.x(x[2])
    
    # Uncompute clause 2
    qc.mcx([x[0], x[3], x[4]], a[1])
    
    # Uncompute clause 1
    qc.x(x[3])
    qc.mcx([x[1], x[2], x[3]], a[0])
    qc.x(x[3])
