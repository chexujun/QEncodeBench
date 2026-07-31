from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x = problem_qubits
    a = ancilla_qubits
    
    # Initialize clause ancillas to 1
    for i in range(5):
        qc.x(a[i])
    
    # Clause 1: (NOT x0 OR x2 OR x3) false when x0=1, x2=0, x3=0
    qc.x(x[2])
    qc.x(x[3])
    qc.mcx([x[0], x[2], x[3]], a[0])
    qc.x(x[3])
    qc.x(x[2])
    
    # Clause 2: (x0 OR NOT x1 OR NOT x2) false when x0=0, x1=1, x2=1
    qc.x(x[0])
    qc.mcx([x[0], x[1], x[2]], a[1])
    qc.x(x[0])
    
    # Clause 3: (NOT x0 OR NOT x1 OR NOT x2) false when x0=1, x1=1, x2=1
    qc.mcx([x[0], x[1], x[2]], a[2])
    
    # Clause 4: (x0 OR NOT x1 OR x3) false when x0=0, x1=1, x3=0
    qc.x(x[0])
    qc.x(x[3])
    qc.mcx([x[0], x[1], x[3]], a[3])
    qc.x(x[3])
    qc.x(x[0])
    
    # Clause 5: (x0 OR x1 OR x3) false when x0=0, x1=0, x3=0
    qc.x(x[0])
    qc.x(x[1])
    qc.x(x[3])
    qc.mcx([x[0], x[1], x[3]], a[4])
    qc.x(x[3])
    qc.x(x[1])
    qc.x(x[0])
    
    # AND all clauses into final ancilla
    qc.mcx([a[0], a[1], a[2], a[3], a[4]], a[5])
    
    # Apply phase flip
    qc.z(a[5])
    
    # Uncompute: AND back
    qc.mcx([a[0], a[1], a[2], a[3], a[4]], a[5])
    
    # Undo clause conditions in reverse order
    qc.x(x[0])
    qc.x(x[1])
    qc.x(x[3])
    qc.mcx([x[0], x[1], x[3]], a[4])
    qc.x(x[3])
    qc.x(x[1])
    qc.x(x[0])
    
    qc.x(x[0])
    qc.x(x[3])
    qc.mcx([x[0], x[1], x[3]], a[3])
    qc.x(x[3])
    qc.x(x[0])
    
    qc.mcx([x[0], x[1], x[2]], a[2])
    
    qc.x(x[0])
    qc.mcx([x[0], x[1], x[2]], a[1])
    qc.x(x[0])
    
    qc.x(x[2])
    qc.x(x[3])
    qc.mcx([x[0], x[2], x[3]], a[0])
    qc.x(x[3])
    qc.x(x[2])
    
    # Uninitialize clause ancillas
    for i in range(5):
        qc.x(a[i])
