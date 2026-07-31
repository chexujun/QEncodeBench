from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    x = problem_qubits  # x[0] through x[5]
    c = ancilla_qubits  # c[0] through c[6]
    
    # === COMPUTE CLAUSES ===
    
    # Clause 1: NOT(x2 AND x3 AND x5) → c[0]
    qc.x(c[0])
    qc.mcx([x[2], x[3], x[5]], c[0])
    
    # Clause 4: NOT(x0 AND x1 AND x4) → c[3]
    qc.x(c[3])
    qc.mcx([x[0], x[1], x[4]], c[3])
    
    # Clause 2: NOT(x0 AND NOT x3 AND NOT x5) → c[1]
    qc.x(c[6])
    qc.cx(x[3], c[6])  # c[6] = NOT x3
    qc.x(c[5])
    qc.cx(x[5], c[5])  # c[5] = NOT x5
    qc.x(c[1])
    qc.mcx([x[0], c[6], c[5]], c[1])
    # Uncompute temps
    qc.cx(x[5], c[5])
    qc.x(c[5])
    qc.cx(x[3], c[6])
    qc.x(c[6])
    
    # Clause 3: NOT(NOT x1 AND NOT x4 AND NOT x5) → c[2]
    qc.x(c[6])
    qc.cx(x[1], c[6])  # c[6] = NOT x1
    qc.x(c[4])
    qc.cx(x[4], c[4])  # c[4] = NOT x4
    qc.x(c[5])
    qc.cx(x[5], c[5])  # c[5] = NOT x5
    qc.x(c[2])
    qc.mcx([c[6], c[4], c[5]], c[2])
    # Uncompute temps
    qc.cx(x[5], c[5])
    qc.x(c[5])
    qc.cx(x[4], c[4])
    qc.x(c[4])
    qc.cx(x[1], c[6])
    qc.x(c[6])
    
    # Clause 5: NOT(NOT x0 AND NOT x1 AND NOT x2) → c[4]
    qc.x(c[6])
    qc.cx(x[0], c[6])  # c[6] = NOT x0
    qc.x(c[5])
    qc.cx(x[1], c[5])  # c[5] = NOT x1
    qc.x(c[2])
    qc.cx(x[2], c[2])  # c[2] = NOT x2
    qc.x(c[4])
    qc.mcx([c[6], c[5], c[2]], c[4])
    # Uncompute temps
    qc.cx(x[2], c[2])
    qc.x(c[2])
    qc.cx(x[1], c[5])
    qc.x(c[5])
    qc.cx(x[0], c[6])
    qc.x(c[6])
    
    # Clause 6: NOT(NOT x0 AND x1 AND NOT x5) → c[5]
    qc.x(c[6])
    qc.cx(x[0], c[6])  # c[6] = NOT x0
    qc.x(c[2])
    qc.cx(x[5], c[2])  # c[2] = NOT x5
    qc.x(c[5])
    qc.mcx([c[6], x[1], c[2]], c[5])
    # Uncompute temps
    qc.cx(x[5], c[2])
    qc.x(c[2])
    qc.cx(x[0], c[6])
    qc.x(c[6])
    
    # === COMPUTE AND OF ALL CLAUSES ===
    qc.mcx([c[0], c[1], c[2], c[3], c[4], c[5]], c[6])
    
    # === APPLY PHASE ===
    qc.z(c[6])
    
    # === UNCOMPUTE AND ===
    qc.mcx([c[0], c[1], c[2], c[3], c[4], c[5]], c[6])
    
    # === UNCOMPUTE CLAUSES (REVERSE ORDER) ===
    
    # Uncompute Clause 6
    qc.x(c[6])
    qc.cx(x[0], c[6])
    qc.x(c[2])
    qc.cx(x[5], c[2])
    qc.mcx([c[6], x[1], c[2]], c[5])
    qc.x(c[5])
    qc.cx(x[5], c[2])
    qc.x(c[2])
    qc.cx(x[0], c[6])
    qc.x(c[6])
    
    # Uncompute Clause 5
    qc.x(c[6])
    qc.cx(x[0], c[6])
    qc.x(c[5])
    qc.cx(x[1], c[5])
    qc.x(c[2])
    qc.cx(x[2], c[2])
    qc.mcx([c[6], c[5], c[2]], c[4])
    qc.x(c[4])
    qc.cx(x[2], c[2])
    qc.x(c[2])
    qc.cx(x[1], c[5])
    qc.x(c[5])
    qc.cx(x[0], c[6])
    qc.x(c[6])
    
    # Uncompute Clause 3
    qc.x(c[6])
    qc.cx(x[1], c[6])
    qc.x(c[4])
    qc.cx(x[4], c[4])
    qc.x(c[5])
    qc.cx(x[5], c[5])
    qc.mcx([c[6], c[4], c[5]], c[2])
    qc.x(c[2])
    qc.cx(x[5], c[5])
    qc.x(c[5])
    qc.cx(x[4], c[4])
    qc.x(c[4])
    qc.cx(x[1], c[6])
    qc.x(c[6])
    
    # Uncompute Clause 2
    qc.x(c[6])
    qc.cx(x[3], c[6])
    qc.x(c[5])
    qc.cx(x[5], c[5])
    qc.mcx([x[0], c[6], c[5]], c[1])
    qc.x(c[1])
    qc.cx(x[5], c[5])
    qc.x(c[5])
    qc.cx(x[3], c[6])
    qc.x(c[6])
    
    # Uncompute Clause 4
    qc.mcx([x[0], x[1], x[4]], c[3])
    qc.x(c[3])
    
    # Uncompute Clause 1
    qc.mcx([x[2], x[3], x[5]], c[0])
    qc.x(c[0])
