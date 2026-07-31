from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x0, x1, x2, x3 = problem_qubits
    c1, c2, c3, c4, c5, c6, temp = ancilla_qubits
    
    # Clause 1: (x0 OR x1 OR NOT x2)
    # FALSE iff (NOT x0) AND (NOT x1) AND x2
    qc.x(x0)
    qc.x(x1)
    qc.mcx([x0, x1, x2], temp)
    qc.x(x0)
    qc.x(x1)
    qc.x(c1)
    qc.cx(temp, c1)
    
    # Clause 2: (x0 OR x2 OR NOT x3)
    # FALSE iff (NOT x0) AND (NOT x2) AND x3
    qc.x(x0)
    qc.x(x2)
    qc.mcx([x0, x2, x3], temp)
    qc.x(x0)
    qc.x(x2)
    qc.x(c2)
    qc.cx(temp, c2)
    
    # Clause 3: (NOT x1 OR x2 OR x3)
    # FALSE iff x1 AND (NOT x2) AND (NOT x3)
    qc.x(x2)
    qc.x(x3)
    qc.mcx([x1, x2, x3], temp)
    qc.x(x2)
    qc.x(x3)
    qc.x(c3)
    qc.cx(temp, c3)
    
    # Clause 4: (NOT x0 OR NOT x2 OR NOT x3)
    # FALSE iff x0 AND x2 AND x3
    qc.mcx([x0, x2, x3], temp)
    qc.x(c4)
    qc.cx(temp, c4)
    
    # Clause 5: (NOT x0 OR x2 OR x3)
    # FALSE iff x0 AND (NOT x2) AND (NOT x3)
    qc.x(x2)
    qc.x(x3)
    qc.mcx([x0, x2, x3], temp)
    qc.x(x2)
    qc.x(x3)
    qc.x(c5)
    qc.cx(temp, c5)
    
    # Clause 6: (x1 OR x2 OR x3)
    # FALSE iff (NOT x1) AND (NOT x2) AND (NOT x3)
    qc.x(x1)
    qc.x(x2)
    qc.x(x3)
    qc.mcx([x1, x2, x3], temp)
    qc.x(x1)
    qc.x(x2)
    qc.x(x3)
    qc.x(c6)
    qc.cx(temp, c6)
    
    # Compute AND of all clause satisfactions into temp
    qc.mcx([c1, c2, c3, c4, c5, c6], temp)
    
    # Apply phase -1 when all clauses satisfied
    qc.z(temp)
    
    # Uncompute AND
    qc.mcx([c1, c2, c3, c4, c5, c6], temp)
    
    # Uncompute clause 6
    qc.cx(temp, c6)
    qc.x(c6)
    qc.x(x1)
    qc.x(x2)
    qc.x(x3)
    qc.mcx([x1, x2, x3], temp)
    qc.x(x1)
    qc.x(x2)
    qc.x(x3)
    
    # Uncompute clause 5
    qc.cx(temp, c5)
    qc.x(c5)
    qc.x(x2)
    qc.x(x3)
    qc.mcx([x0, x2, x3], temp)
    qc.x(x2)
    qc.x(x3)
    
    # Uncompute clause 4
    qc.cx(temp, c4)
    qc.x(c4)
    qc.mcx([x0, x2, x3], temp)
    
    # Uncompute clause 3
    qc.cx(temp, c3)
    qc.x(c3)
    qc.x(x2)
    qc.x(x3)
    qc.mcx([x1, x2, x3], temp)
    qc.x(x2)
    qc.x(x3)
    
    # Uncompute clause 2
    qc.cx(temp, c2)
    qc.x(c2)
    qc.x(x0)
    qc.x(x2)
    qc.mcx([x0, x2, x3], temp)
    qc.x(x0)
    qc.x(x2)
    
    # Uncompute clause 1
    qc.cx(temp, c1)
    qc.x(c1)
    qc.x(x0)
    qc.x(x1)
    qc.mcx([x0, x1, x2], temp)
    qc.x(x0)
    qc.x(x1)
