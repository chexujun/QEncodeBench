from math import pi

def build_oracle(qc, problem_qubits, ancilla_qubits):
    x = problem_qubits
    a = ancilla_qubits
    
    # === COMPUTE ===
    
    # Clause 1: (NOT x1 OR x3 OR x4) = NOT(x1 AND NOT x3 AND NOT x4)
    qc.x(x[3])
    qc.x(x[4])
    qc.mcx([x[1], x[3], x[4]], a[0])
    qc.x(x[3])
    qc.x(x[4])
    qc.x(a[0])
    
    # Clause 2: (x1 OR x5 OR NOT x6) = NOT(NOT x1 AND NOT x5 AND x6)
    qc.x(x[1])
    qc.x(x[5])
    qc.mcx([x[1], x[5], x[6]], a[1])
    qc.x(x[1])
    qc.x(x[5])
    qc.x(a[1])
    
    # Clause 3: (NOT x0 OR NOT x3 OR NOT x4) = NOT(x0 AND x3 AND x4)
    qc.mcx([x[0], x[3], x[4]], a[2])
    qc.x(a[2])
    
    # Clause 4: (NOT x0 OR NOT x1 OR NOT x6) = NOT(x0 AND x1 AND x6)
    qc.mcx([x[0], x[1], x[6]], a[3])
    qc.x(a[3])
    
    # Clause 5: (x1 OR NOT x4 OR x6) = NOT(NOT x1 AND x4 AND NOT x6)
    qc.x(x[1])
    qc.x(x[6])
    qc.mcx([x[1], x[4], x[6]], a[4])
    qc.x(x[1])
    qc.x(x[6])
    qc.x(a[4])
    
    # Clause 6: (NOT x0 OR NOT x1 OR x3) = NOT(x0 AND x1 AND NOT x3)
    qc.x(x[3])
    qc.mcx([x[0], x[1], x[3]], a[5])
    qc.x(x[3])
    qc.x(a[5])
    
    # Clause 7: (x2 OR NOT x5 OR NOT x6) = NOT(NOT x2 AND x5 AND x6)
    qc.x(x[2])
    qc.mcx([x[2], x[5], x[6]], a[6])
    qc.x(x[2])
    qc.x(a[6])
    
    # === PHASE ===
    # Apply Z phase controlled by all clause ancillas
    qc.mcp(pi, [a[0], a[1], a[2], a[3], a[4], a[5], a[6]])
    
    # === UNCOMPUTE ===
    
    # Clause 7
    qc.x(a[6])
    qc.x(x[2])
    qc.mcx([x[2], x[5], x[6]], a[6])
    qc.x(x[2])
    
    # Clause 6
    qc.x(a[5])
    qc.x(x[3])
    qc.mcx([x[0], x[1], x[3]], a[5])
    qc.x(x[3])
    
    # Clause 5
    qc.x(a[4])
    qc.x(x[1])
    qc.x(x[6])
    qc.mcx([x[1], x[4], x[6]], a[4])
    qc.x(x[1])
    qc.x(x[6])
    
    # Clause 4
    qc.x(a[3])
    qc.mcx([x[0], x[1], x[6]], a[3])
    
    # Clause 3
    qc.x(a[2])
    qc.mcx([x[0], x[3], x[4]], a[2])
    
    # Clause 2
    qc.x(a[1])
    qc.x(x[1])
    qc.x(x[5])
    qc.mcx([x[1], x[5], x[6]], a[1])
    qc.x(x[1])
    qc.x(x[5])
    
    # Clause 1
    qc.x(a[0])
    qc.x(x[3])
    qc.x(x[4])
    qc.mcx([x[1], x[3], x[4]], a[0])
    qc.x(x[3])
    qc.x(x[4])
