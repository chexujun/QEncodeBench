from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x = problem_qubits  # x[0] to x[5]
    clause_false = ancilla_qubits[0:7]  # One ancilla per clause
    result = ancilla_qubits[7]  # Final phase ancilla
    
    # Compute whether each clause is FALSE into clause_false[i]
    # Clause 1: (NOT x0 OR NOT x2 OR x4) is FALSE when x0=1, x2=1, x4=0
    qc.x(x[4])
    qc.mcx([x[0], x[2], x[4]], clause_false[0])
    qc.x(x[4])
    
    # Clause 2: (x2 OR x4 OR NOT x5) is FALSE when x2=0, x4=0, x5=1
    qc.x(x[2])
    qc.x(x[4])
    qc.mcx([x[2], x[4], x[5]], clause_false[1])
    qc.x(x[4])
    qc.x(x[2])
    
    # Clause 3: (x1 OR x2 OR NOT x4) is FALSE when x1=0, x2=0, x4=1
    qc.x(x[1])
    qc.x(x[2])
    qc.mcx([x[1], x[2], x[4]], clause_false[2])
    qc.x(x[2])
    qc.x(x[1])
    
    # Clause 4: (x1 OR x2 OR NOT x5) is FALSE when x1=0, x2=0, x5=1
    qc.x(x[1])
    qc.x(x[2])
    qc.mcx([x[1], x[2], x[5]], clause_false[3])
    qc.x(x[2])
    qc.x(x[1])
    
    # Clause 5: (NOT x0 OR NOT x1 OR NOT x4) is FALSE when x0=1, x1=1, x4=1
    qc.mcx([x[0], x[1], x[4]], clause_false[4])
    
    # Clause 6: (x0 OR x2 OR x4) is FALSE when x0=0, x2=0, x4=0
    qc.x(x[0])
    qc.x(x[2])
    qc.x(x[4])
    qc.mcx([x[0], x[2], x[4]], clause_false[5])
    qc.x(x[4])
    qc.x(x[2])
    qc.x(x[0])
    
    # Clause 7: (NOT x0 OR NOT x4 OR x5) is FALSE when x0=1, x4=1, x5=0
    qc.x(x[5])
    qc.mcx([x[0], x[4], x[5]], clause_false[6])
    qc.x(x[5])
    
    # Negate all clause_false values so we detect when all are 0 (all clauses true)
    for i in range(7):
        qc.x(clause_false[i])
    
    # Multi-controlled X: flip result if all negated clause_false are 1
    qc.mcx(clause_false, result)
    
    # Restore clause_false values
    for i in range(7):
        qc.x(clause_false[i])
    
    # Apply phase flip
    qc.z(result)
    
    # Uncompute: negate controls again
    for i in range(7):
        qc.x(clause_false[i])
    
    qc.mcx(clause_false, result)
    
    for i in range(7):
        qc.x(clause_false[i])
    
    # Uncompute clause computations in reverse order
    qc.x(x[5])
    qc.mcx([x[0], x[4], x[5]], clause_false[6])
    qc.x(x[5])
    
    qc.x(x[0])
    qc.x(x[2])
    qc.x(x[4])
    qc.mcx([x[0], x[2], x[4]], clause_false[5])
    qc.x(x[4])
    qc.x(x[2])
    qc.x(x[0])
    
    qc.mcx([x[0], x[1], x[4]], clause_false[4])
    
    qc.x(x[1])
    qc.x(x[2])
    qc.mcx([x[1], x[2], x[5]], clause_false[3])
    qc.x(x[2])
    qc.x(x[1])
    
    qc.x(x[1])
    qc.x(x[2])
    qc.mcx([x[1], x[2], x[4]], clause_false[2])
    qc.x(x[2])
    qc.x(x[1])
    
    qc.x(x[2])
    qc.x(x[4])
    qc.mcx([x[2], x[4], x[5]], clause_false[1])
    qc.x(x[4])
    qc.x(x[2])
    
    qc.x(x[4])
    qc.mcx([x[0], x[2], x[4]], clause_false[0])
    qc.x(x[4])
