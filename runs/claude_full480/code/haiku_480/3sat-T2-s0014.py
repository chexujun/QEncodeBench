from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    x0, x1, x2, x3 = problem_qubits[0:4]
    a0, a1, a2, a3, a4, a5, a6 = ancilla_qubits[0:7]
    
    # Clause 1: (x0 OR x1 OR NOT x2)
    # NOT clause = (NOT x0) AND (NOT x1) AND x2, true when x0=0, x1=0, x2=1
    qc.x(x0)
    qc.x(x1)
    qc.mcx([x0, x1, x2], a0)
    qc.x(x1)
    qc.x(x0)
    qc.x(a0)
    
    # Clause 2: (x1 OR NOT x2 OR NOT x3)
    # NOT clause = (NOT x1) AND x2 AND x3, true when x1=0, x2=1, x3=1
    qc.x(x1)
    qc.mcx([x1, x2, x3], a1)
    qc.x(x1)
    qc.x(a1)
    
    # Clause 3: (NOT x1 OR x2 OR x3)
    # NOT clause = x1 AND (NOT x2) AND (NOT x3), true when x1=1, x2=0, x3=0
    qc.x(x2)
    qc.x(x3)
    qc.mcx([x1, x2, x3], a2)
    qc.x(x3)
    qc.x(x2)
    qc.x(a2)
    
    # Clause 4: (NOT x0 OR NOT x2 OR x3)
    # NOT clause = x0 AND x2 AND (NOT x3), true when x0=1, x2=1, x3=0
    qc.x(x3)
    qc.mcx([x0, x2, x3], a3)
    qc.x(x3)
    qc.x(a3)
    
    # Clause 5: (x0 OR x2 OR NOT x3)
    # NOT clause = (NOT x0) AND (NOT x2) AND x3, true when x0=0, x2=0, x3=1
    qc.x(x0)
    qc.x(x2)
    qc.mcx([x0, x2, x3], a4)
    qc.x(x2)
    qc.x(x0)
    qc.x(a4)
    
    # Clause 6: (x0 OR NOT x1 OR x2)
    # NOT clause = (NOT x0) AND x1 AND (NOT x2), true when x0=0, x1=1, x2=0
    qc.x(x0)
    qc.x(x2)
    qc.mcx([x0, x1, x2], a5)
    qc.x(x2)
    qc.x(x0)
    qc.x(a5)
    
    # AND all clause results into a6
    qc.mcx([a0, a1, a2, a3, a4, a5], a6)
    
    # Phase flip
    qc.z(a6)
    
    # Uncompute
    qc.mcx([a0, a1, a2, a3, a4, a5], a6)
    
    qc.x(a5)
    qc.x(x0)
    qc.x(x2)
    qc.mcx([x0, x1, x2], a5)
    qc.x(x2)
    qc.x(x0)
    
    qc.x(a4)
    qc.x(x0)
    qc.x(x2)
    qc.mcx([x0, x2, x3], a4)
    qc.x(x2)
    qc.x(x0)
    
    qc.x(a3)
    qc.x(x3)
    qc.mcx([x0, x2, x3], a3)
    qc.x(x3)
    
    qc.x(a2)
    qc.x(x2)
    qc.x(x3)
    qc.mcx([x1, x2, x3], a2)
    qc.x(x3)
    qc.x(x2)
    
    qc.x(a1)
    qc.x(x1)
    qc.mcx([x1, x2, x3], a1)
    qc.x(x1)
    
    qc.x(a0)
    qc.x(x0)
    qc.x(x1)
    qc.mcx([x0, x1, x2], a0)
    qc.x(x1)
    qc.x(x0)
