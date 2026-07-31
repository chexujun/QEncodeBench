from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x = problem_qubits
    a = ancilla_qubits
    
    # Compute unsatisfied flags for each clause
    # Clause 0: (NOT x0 OR x1 OR NOT x2) - unsatisfied when x0=1 AND x1=0 AND x2=1
    qc.x(x[1])
    qc.mcx([x[0], x[1], x[2]], a[0])
    qc.x(x[1])
    
    # Clause 1: (NOT x1 OR x2 OR x4) - unsatisfied when x1=1 AND x2=0 AND x4=0
    qc.x(x[2])
    qc.x(x[4])
    qc.mcx([x[1], x[2], x[4]], a[1])
    qc.x(x[4])
    qc.x(x[2])
    
    # Clause 2: (x0 OR NOT x1 OR x3) - unsatisfied when x0=0 AND x1=1 AND x3=0
    qc.x(x[0])
    qc.x(x[3])
    qc.mcx([x[0], x[1], x[3]], a[2])
    qc.x(x[3])
    qc.x(x[0])
    
    # Clause 3: (NOT x1 OR x3 OR NOT x4) - unsatisfied when x1=1 AND x3=0 AND x4=1
    qc.x(x[3])
    qc.mcx([x[1], x[3], x[4]], a[3])
    qc.x(x[3])
    
    # Clause 4: (x1 OR NOT x2 OR NOT x3) - unsatisfied when x1=0 AND x2=1 AND x3=1
    qc.x(x[1])
    qc.mcx([x[1], x[2], x[3]], a[4])
    qc.x(x[1])
    
    # Clause 5: (NOT x1 OR NOT x3 OR x4) - unsatisfied when x1=1 AND x3=1 AND x4=0
    qc.x(x[4])
    qc.mcx([x[1], x[3], x[4]], a[5])
    qc.x(x[4])
    
    # Compute OR of all unsatisfied flags into a[6]
    qc.cx(a[0], a[6])
    for i in range(1, 6):
        qc.x(a[6])
        qc.ccx(a[i], a[6], a[6])
        qc.x(a[6])
    
    # Apply -1 phase to states where a[6]=0 (all clauses satisfied)
    qc.x(a[6])
    qc.z(a[6])
    qc.x(a[6])
    
    # Uncompute OR
    for i in range(5, 0, -1):
        qc.x(a[6])
        qc.ccx(a[i], a[6], a[6])
        qc.x(a[6])
    qc.cx(a[0], a[6])
    
    # Uncompute unsatisfied flags
    qc.x(x[4])
    qc.mcx([x[1], x[3], x[4]], a[5])
    qc.x(x[4])
    
    qc.x(x[1])
    qc.mcx([x[1], x[2], x[3]], a[4])
    qc.x(x[1])
    
    qc.x(x[3])
    qc.mcx([x[1], x[3], x[4]], a[3])
    qc.x(x[3])
    
    qc.x(x[0])
    qc.x(x[3])
    qc.mcx([x[0], x[1], x[3]], a[2])
    qc.x(x[3])
    qc.x(x[0])
    
    qc.x(x[2])
    qc.x(x[4])
    qc.mcx([x[1], x[2], x[4]], a[1])
    qc.x(x[4])
    qc.x(x[2])
    
    qc.x(x[1])
    qc.mcx([x[0], x[1], x[2]], a[0])
    qc.x(x[1])
