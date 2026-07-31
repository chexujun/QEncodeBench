from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x0, x1, x2, x3 = problem_qubits
    a1, a2, a3, a4, a5, a6, a_final = ancilla_qubits
    
    # === COMPUTE PHASE ===
    
    # Clause 1: (NOT x0 OR NOT x2 OR x3)
    # Compute NOT(clause) = x0 AND x2 AND NOT x3 into a1, then flip a1
    qc.x(x3)
    qc.mcx([x0, x2, x3], a1)
    qc.x(x3)
    qc.x(a1)
    
    # Clause 2: (x0 OR x1 OR x2)
    # Compute NOT(clause) = NOT x0 AND NOT x1 AND NOT x2
    qc.x(x0)
    qc.x(x1)
    qc.x(x2)
    qc.mcx([x0, x1, x2], a2)
    qc.x(x2)
    qc.x(x1)
    qc.x(x0)
    qc.x(a2)
    
    # Clause 3: (x0 OR NOT x1 OR NOT x2)
    # Compute NOT(clause) = NOT x0 AND x1 AND x2
    qc.x(x0)
    qc.mcx([x0, x1, x2], a3)
    qc.x(x0)
    qc.x(a3)
    
    # Clause 4: (NOT x0 OR x1 OR x2)
    # Compute NOT(clause) = x0 AND NOT x1 AND NOT x2
    qc.x(x1)
    qc.x(x2)
    qc.mcx([x0, x1, x2], a4)
    qc.x(x2)
    qc.x(x1)
    qc.x(a4)
    
    # Clause 5: (NOT x0 OR x1 OR NOT x2)
    # Compute NOT(clause) = x0 AND NOT x1 AND x2
    qc.x(x1)
    qc.mcx([x0, x1, x2], a5)
    qc.x(x1)
    qc.x(a5)
    
    # Clause 6: (x1 OR x2 OR x3)
    # Compute NOT(clause) = NOT x1 AND NOT x2 AND NOT x3
    qc.x(x1)
    qc.x(x2)
    qc.x(x3)
    qc.mcx([x1, x2, x3], a6)
    qc.x(x3)
    qc.x(x2)
    qc.x(x1)
    qc.x(a6)
    
    # Compute AND of all clauses into a_final
    qc.mcx([a1, a2, a3, a4, a5, a6], a_final)
    
    # === PHASE ===
    qc.z(a_final)
    
    # === UNCOMPUTE ===
    
    # Uncompute AND
    qc.mcx([a1, a2, a3, a4, a5, a6], a_final)
    
    # Uncompute clause 6
    qc.x(a6)
    qc.x(x1)
    qc.x(x2)
    qc.x(x3)
    qc.mcx([x1, x2, x3], a6)
    qc.x(x3)
    qc.x(x2)
    qc.x(x1)
    
    # Uncompute clause 5
    qc.x(a5)
    qc.x(x1)
    qc.mcx([x0, x1, x2], a5)
    qc.x(x1)
    
    # Uncompute clause 4
    qc.x(a4)
    qc.x(x1)
    qc.x(x2)
    qc.mcx([x0, x1, x2], a4)
    qc.x(x2)
    qc.x(x1)
    
    # Uncompute clause 3
    qc.x(a3)
    qc.x(x0)
    qc.mcx([x0, x1, x2], a3)
    qc.x(x0)
    
    # Uncompute clause 2
    qc.x(a2)
    qc.x(x0)
    qc.x(x1)
    qc.x(x2)
    qc.mcx([x0, x1, x2], a2)
    qc.x(x2)
    qc.x(x1)
    qc.x(x0)
    
    # Uncompute clause 1
    qc.x(a1)
    qc.x(x3)
    qc.mcx([x0, x2, x3], a1)
    qc.x(x3)
