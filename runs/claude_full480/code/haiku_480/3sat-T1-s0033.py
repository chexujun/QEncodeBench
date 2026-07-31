from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x0, x1, x2, x3 = problem_qubits
    c1, c2, c3, c4, c5, result = ancilla_qubits
    
    # Compute clause 1: (NOT x0 OR x1 OR x3) = NOT(x0 AND NOT x1 AND NOT x3)
    qc.x(x1); qc.x(x3)
    qc.mcx([x0, x1, x3], c1)
    qc.x(x3); qc.x(x1)
    qc.x(c1)
    
    # Compute clause 2: (NOT x0 OR x1 OR NOT x2) = NOT(x0 AND NOT x1 AND x2)
    qc.x(x1)
    qc.mcx([x0, x1, x2], c2)
    qc.x(x1)
    qc.x(c2)
    
    # Compute clause 3: (x0 OR NOT x1 OR x3) = NOT(NOT x0 AND x1 AND NOT x3)
    qc.x(x0); qc.x(x3)
    qc.mcx([x0, x1, x3], c3)
    qc.x(x3); qc.x(x0)
    qc.x(c3)
    
    # Compute clause 4: (NOT x0 OR x2 OR x3) = NOT(x0 AND NOT x2 AND NOT x3)
    qc.x(x2); qc.x(x3)
    qc.mcx([x0, x2, x3], c4)
    qc.x(x3); qc.x(x2)
    qc.x(c4)
    
    # Compute clause 5: (NOT x0 OR NOT x1 OR NOT x3) = NOT(x0 AND x1 AND x3)
    qc.mcx([x0, x1, x3], c5)
    qc.x(c5)
    
    # Apply phase if all clauses are true (AND them together with Z gate)
    qc.mcx([c1, c2, c3, c4, c5], result)
    qc.z(result)
    qc.mcx([c1, c2, c3, c4, c5], result)
    
    # Uncompute clause 5
    qc.x(c5)
    qc.mcx([x0, x1, x3], c5)
    
    # Uncompute clause 4
    qc.x(c4)
    qc.x(x2); qc.x(x3)
    qc.mcx([x0, x2, x3], c4)
    qc.x(x3); qc.x(x2)
    
    # Uncompute clause 3
    qc.x(c3)
    qc.x(x0); qc.x(x3)
    qc.mcx([x0, x1, x3], c3)
    qc.x(x3); qc.x(x0)
    
    # Uncompute clause 2
    qc.x(c2)
    qc.x(x1)
    qc.mcx([x0, x1, x2], c2)
    qc.x(x1)
    
    # Uncompute clause 1
    qc.x(c1)
    qc.x(x1); qc.x(x3)
    qc.mcx([x0, x1, x3], c1)
    qc.x(x3); qc.x(x1)
