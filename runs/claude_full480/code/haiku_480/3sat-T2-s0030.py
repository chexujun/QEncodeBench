from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    x0, x1, x2, x3 = problem_qubits[0], problem_qubits[1], problem_qubits[2], problem_qubits[3]
    a0, a1, a2, a3, a4, a5, a6 = ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[2], ancilla_qubits[3], ancilla_qubits[4], ancilla_qubits[5], ancilla_qubits[6]
    
    # COMPUTE: Evaluate whether each clause is violated (0 means satisfied, 1 means violated)
    
    # Clause 0: (NOT x0 OR x2 OR NOT x3) - violated iff x0=1 AND x2=0 AND x3=1
    qc.x(x2)
    qc.mcx([x0, x2, x3], a0)
    qc.x(x2)
    
    # Clause 1: (x0 OR x1 OR NOT x2) - violated iff x0=0 AND x1=0 AND x2=1
    qc.x(x0)
    qc.x(x1)
    qc.mcx([x0, x1, x2], a1)
    qc.x(x1)
    qc.x(x0)
    
    # Clause 2: (NOT x0 OR x1 OR x2) - violated iff x0=1 AND x1=0 AND x2=0
    qc.x(x1)
    qc.x(x2)
    qc.mcx([x0, x1, x2], a2)
    qc.x(x2)
    qc.x(x1)
    
    # Clause 3: (x0 OR x1 OR x2) - violated iff x0=0 AND x1=0 AND x2=0
    qc.x(x0)
    qc.x(x1)
    qc.x(x2)
    qc.mcx([x0, x1, x2], a3)
    qc.x(x2)
    qc.x(x1)
    qc.x(x0)
    
    # Clause 4: (x0 OR NOT x2 OR x3) - violated iff x0=0 AND x2=1 AND x3=0
    qc.x(x0)
    qc.x(x3)
    qc.mcx([x0, x2, x3], a4)
    qc.x(x3)
    qc.x(x0)
    
    # Clause 5: (x0 OR NOT x2 OR NOT x3) - violated iff x0=0 AND x2=1 AND x3=1
    qc.x(x0)
    qc.mcx([x0, x2, x3], a5)
    qc.x(x0)
    
    # Compute a6 = NOT(a0 OR a1 OR ... OR a5) = AND(NOT a0, NOT a1, ..., NOT a5)
    # This equals 1 if and only if all clauses are satisfied
    qc.x(a0)
    qc.x(a1)
    qc.x(a2)
    qc.x(a3)
    qc.x(a4)
    qc.x(a5)
    qc.mcx([a0, a1, a2, a3, a4, a5], a6)
    qc.x(a5)
    qc.x(a4)
    qc.x(a3)
    qc.x(a2)
    qc.x(a1)
    qc.x(a0)
    
    # PHASE: Apply Z to a6 (flips phase -1 when a6=1, i.e., when all clauses satisfied)
    qc.z(a6)
    
    # UNCOMPUTE: Reverse order
    
    # Uncompute a6
    qc.x(a0)
    qc.x(a1)
    qc.x(a2)
    qc.x(a3)
    qc.x(a4)
    qc.x(a5)
    qc.mcx([a0, a1, a2, a3, a4, a5], a6)
    qc.x(a5)
    qc.x(a4)
    qc.x(a3)
    qc.x(a2)
    qc.x(a1)
    qc.x(a0)
    
    # Uncompute clause violations (reverse order)
    qc.x(x0)
    qc.mcx([x0, x2, x3], a5)
    qc.x(x0)
    
    qc.x(x0)
    qc.x(x3)
    qc.mcx([x0, x2, x3], a4)
    qc.x(x3)
    qc.x(x0)
    
    qc.x(x0)
    qc.x(x1)
    qc.x(x2)
    qc.mcx([x0, x1, x2], a3)
    qc.x(x2)
    qc.x(x1)
    qc.x(x0)
    
    qc.x(x1)
    qc.x(x2)
    qc.mcx([x0, x1, x2], a2)
    qc.x(x2)
    qc.x(x1)
    
    qc.x(x0)
    qc.x(x1)
    qc.mcx([x0, x1, x2], a1)
    qc.x(x1)
    qc.x(x0)
    
    qc.x(x2)
    qc.mcx([x0, x2, x3], a0)
    qc.x(x2)
