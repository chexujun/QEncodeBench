from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x0, x1, x2, x3, x4, x5 = problem_qubits
    a0, a1, a2, a3, a4, a5, a6 = ancilla_qubits
    
    # Compute each clause into an ancilla
    # C0: (NOT x1 OR NOT x2 OR NOT x5) = NOT(x1 AND x2 AND x5)
    qc.x(a0)
    qc.mcx([x1, x2, x5], a0)
    
    # C1: (x0 OR x3 OR x5) = NOT(NOT x0 AND NOT x3 AND NOT x5)
    qc.x(a1)
    qc.x(x0)
    qc.x(x3)
    qc.x(x5)
    qc.mcx([x0, x3, x5], a1)
    qc.x(x0)
    qc.x(x3)
    qc.x(x5)
    
    # C2: (x1 OR x2 OR NOT x4) = NOT(NOT x1 AND NOT x2 AND x4)
    qc.x(a2)
    qc.x(x1)
    qc.x(x2)
    qc.mcx([x1, x2, x4], a2)
    qc.x(x1)
    qc.x(x2)
    
    # C3: (x2 OR x3 OR NOT x4) = NOT(NOT x2 AND NOT x3 AND x4)
    qc.x(a3)
    qc.x(x2)
    qc.x(x3)
    qc.mcx([x2, x3, x4], a3)
    qc.x(x2)
    qc.x(x3)
    
    # C4: (NOT x1 OR x4 OR NOT x5) = NOT(x1 AND NOT x4 AND x5)
    qc.x(a4)
    qc.x(x4)
    qc.mcx([x1, x4, x5], a4)
    qc.x(x4)
    
    # C5: (NOT x3 OR NOT x4 OR x5) = NOT(x3 AND x4 AND NOT x5)
    qc.x(a5)
    qc.x(x5)
    qc.mcx([x3, x4, x5], a5)
    qc.x(x5)
    
    # Compute: a6 = (a0 AND a1 AND a2 AND a3 AND a4 AND a5)
    qc.x(a6)
    qc.mcx([a0, a1, a2, a3, a4, a5], a6)
    qc.x(a6)
    
    # Apply phase
    qc.z(a6)
    
    # Uncompute a6
    qc.x(a6)
    qc.mcx([a0, a1, a2, a3, a4, a5], a6)
    qc.x(a6)
    
    # Uncompute all clauses in reverse order
    # C5
    qc.x(x5)
    qc.mcx([x3, x4, x5], a5)
    qc.x(x5)
    qc.x(a5)
    
    # C4
    qc.x(x4)
    qc.mcx([x1, x4, x5], a4)
    qc.x(x4)
    qc.x(a4)
    
    # C3
    qc.x(x2)
    qc.x(x3)
    qc.mcx([x2, x3, x4], a3)
    qc.x(x2)
    qc.x(x3)
    qc.x(a3)
    
    # C2
    qc.x(x1)
    qc.x(x2)
    qc.mcx([x1, x2, x4], a2)
    qc.x(x1)
    qc.x(x2)
    qc.x(a2)
    
    # C1
    qc.x(x0)
    qc.x(x3)
    qc.x(x5)
    qc.mcx([x0, x3, x5], a1)
    qc.x(x0)
    qc.x(x3)
    qc.x(x5)
    qc.x(a1)
    
    # C0
    qc.mcx([x1, x2, x5], a0)
    qc.x(a0)
