from qiskit import QuantumCircuit

def build_oracle(qc, problem_qubits, ancilla_qubits):
    x = problem_qubits
    c = ancilla_qubits[:8]  # clause ancillas
    r = ancilla_qubits[8]   # result ancilla
    
    # Compute all clauses
    
    # Clause 0: (NOT x1 OR x5 OR x6) = NOT(x1 AND NOT x5 AND NOT x6)
    qc.x(x[5])
    qc.x(x[6])
    qc.mcx([x[1], x[5], x[6]], c[0])
    qc.x(c[0])
    qc.x(x[6])
    qc.x(x[5])
    
    # Clause 1: (x1 OR x3 OR x5) = NOT(NOT x1 AND NOT x3 AND NOT x5)
    qc.x(x[1])
    qc.x(x[3])
    qc.x(x[5])
    qc.mcx([x[1], x[3], x[5]], c[1])
    qc.x(c[1])
    qc.x(x[5])
    qc.x(x[3])
    qc.x(x[1])
    
    # Clause 2: (x0 OR x2 OR x4) = NOT(NOT x0 AND NOT x2 AND NOT x4)
    qc.x(x[0])
    qc.x(x[2])
    qc.x(x[4])
    qc.mcx([x[0], x[2], x[4]], c[2])
    qc.x(c[2])
    qc.x(x[4])
    qc.x(x[2])
    qc.x(x[0])
    
    # Clause 3: (x1 OR NOT x2 OR x4) = NOT(NOT x1 AND x2 AND NOT x4)
    qc.x(x[1])
    qc.x(x[4])
    qc.mcx([x[1], x[2], x[4]], c[3])
    qc.x(c[3])
    qc.x(x[4])
    qc.x(x[1])
    
    # Clause 4: (x0 OR x2 OR NOT x5) = NOT(NOT x0 AND NOT x2 AND x5)
    qc.x(x[0])
    qc.x(x[2])
    qc.mcx([x[0], x[2], x[5]], c[4])
    qc.x(c[4])
    qc.x(x[2])
    qc.x(x[0])
    
    # Clause 5: (x1 OR x2 OR x5) = NOT(NOT x1 AND NOT x2 AND NOT x5)
    qc.x(x[1])
    qc.x(x[2])
    qc.x(x[5])
    qc.mcx([x[1], x[2], x[5]], c[5])
    qc.x(c[5])
    qc.x(x[5])
    qc.x(x[2])
    qc.x(x[1])
    
    # Clause 6: (x2 OR x5 OR x6) = NOT(NOT x2 AND NOT x5 AND NOT x6)
    qc.x(x[2])
    qc.x(x[5])
    qc.x(x[6])
    qc.mcx([x[2], x[5], x[6]], c[6])
    qc.x(c[6])
    qc.x(x[6])
    qc.x(x[5])
    qc.x(x[2])
    
    # Clause 7: (NOT x1 OR NOT x2 OR NOT x3) = NOT(x1 AND x2 AND x3)
    qc.mcx([x[1], x[2], x[3]], c[7])
    qc.x(c[7])
    
    # AND all clauses together
    qc.mcx(c, r)
    
    # Apply phase
    qc.z(r)
    
    # Uncompute clauses (reverse order)
    
    # Clause 7
    qc.x(c[7])
    qc.mcx([x[1], x[2], x[3]], c[7])
    
    # Clause 6
    qc.x(x[2])
    qc.x(x[5])
    qc.x(x[6])
    qc.x(c[6])
    qc.mcx([x[2], x[5], x[6]], c[6])
    qc.x(x[6])
    qc.x(x[5])
    qc.x(x[2])
    
    # Clause 5
    qc.x(x[1])
    qc.x(x[2])
    qc.x(x[5])
    qc.x(c[5])
    qc.mcx([x[1], x[2], x[5]], c[5])
    qc.x(x[5])
    qc.x(x[2])
    qc.x(x[1])
    
    # Clause 4
    qc.x(x[0])
    qc.x(x[2])
    qc.x(c[4])
    qc.mcx([x[0], x[2], x[5]], c[4])
    qc.x(x[2])
    qc.x(x[0])
    
    # Clause 3
    qc.x(x[1])
    qc.x(x[4])
    qc.x(c[3])
    qc.mcx([x[1], x[2], x[4]], c[3])
    qc.x(x[4])
    qc.x(x[1])
    
    # Clause 2
    qc.x(x[0])
    qc.x(x[2])
    qc.x(x[4])
    qc.x(c[2])
    qc.mcx([x[0], x[2], x[4]], c[2])
    qc.x(x[4])
    qc.x(x[2])
    qc.x(x[0])
    
    # Clause 1
    qc.x(x[1])
    qc.x(x[3])
    qc.x(x[5])
    qc.x(c[1])
    qc.mcx([x[1], x[3], x[5]], c[1])
    qc.x(x[5])
    qc.x(x[3])
    qc.x(x[1])
    
    # Clause 0
    qc.x(x[5])
    qc.x(x[6])
    qc.x(c[0])
    qc.mcx([x[1], x[5], x[6]], c[0])
    qc.x(x[6])
    qc.x(x[5])
