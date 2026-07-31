from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x0, x1, x2, x3 = problem_qubits[0], problem_qubits[1], problem_qubits[2], problem_qubits[3]
    c1, c2, c3, c4, c5, final = ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[2], ancilla_qubits[3], ancilla_qubits[4], ancilla_qubits[5]
    
    # Clause 1: (NOT x0 OR x1 OR x3)
    # False when x0=1, x1=0, x3=0; compute negation then flip
    qc.x(x1)
    qc.x(x3)
    qc.mcx([x0, x1, x3], c1)
    qc.x(x3)
    qc.x(x1)
    qc.x(c1)
    
    # Clause 2: (x0 OR x1 OR NOT x2)
    # False when x0=0, x1=0, x2=1
    qc.x(x0)
    qc.x(x1)
    qc.mcx([x0, x1, x2], c2)
    qc.x(x1)
    qc.x(x0)
    qc.x(c2)
    
    # Clause 3: (NOT x0 OR x1 OR NOT x2)
    # False when x0=1, x1=0, x2=1
    qc.x(x1)
    qc.mcx([x0, x1, x2], c3)
    qc.x(x1)
    qc.x(c3)
    
    # Clause 4: (NOT x1 OR x2 OR x3)
    # False when x1=1, x2=0, x3=0
    qc.x(x2)
    qc.x(x3)
    qc.mcx([x1, x2, x3], c4)
    qc.x(x3)
    qc.x(x2)
    qc.x(c4)
    
    # Clause 5: (NOT x0 OR NOT x1 OR x2)
    # False when x0=1, x1=1, x2=0
    qc.x(x2)
    qc.mcx([x0, x1, x2], c5)
    qc.x(x2)
    qc.x(c5)
    
    # Compute AND of all clauses
    qc.mcx([c1, c2, c3, c4, c5], final)
    
    # Apply phase
    qc.z(final)
    
    # Uncompute AND
    qc.mcx([c1, c2, c3, c4, c5], final)
    
    # Uncompute Clause 5
    qc.x(c5)
    qc.x(x2)
    qc.mcx([x0, x1, x2], c5)
    qc.x(x2)
    
    # Uncompute Clause 4
    qc.x(c4)
    qc.x(x3)
    qc.x(x2)
    qc.mcx([x1, x2, x3], c4)
    qc.x(x2)
    qc.x(x3)
    
    # Uncompute Clause 3
    qc.x(c3)
    qc.x(x1)
    qc.mcx([x0, x1, x2], c3)
    qc.x(x1)
    
    # Uncompute Clause 2
    qc.x(c2)
    qc.x(x0)
    qc.x(x1)
    qc.mcx([x0, x1, x2], c2)
    qc.x(x1)
    qc.x(x0)
    
    # Uncompute Clause 1
    qc.x(c1)
    qc.x(x1)
    qc.x(x3)
    qc.mcx([x0, x1, x3], c1)
    qc.x(x3)
    qc.x(x1)
