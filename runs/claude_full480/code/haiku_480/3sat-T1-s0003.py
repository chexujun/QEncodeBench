from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x = problem_qubits
    a = ancilla_qubits
    
    # Compute clause negations (a clause is false iff its negation is 1)
    # Clause 1: (NOT x0 OR NOT x1 OR NOT x2) -> negation: (x0 AND x1 AND x2)
    qc.ccx(x[0], x[1], a[0])
    qc.ccx(a[0], x[2], a[1])
    qc.ccx(x[0], x[1], a[0])
    
    # Clause 2: (x0 OR x1 OR x2) -> negation: (NOT x0 AND NOT x1 AND NOT x2)
    qc.x(x[0])
    qc.x(x[1])
    qc.x(x[2])
    qc.ccx(x[0], x[1], a[0])
    qc.ccx(a[0], x[2], a[2])
    qc.ccx(x[0], x[1], a[0])
    qc.x(x[0])
    qc.x(x[1])
    qc.x(x[2])
    
    # Clause 3: (x0 OR x1 OR NOT x2) -> negation: (NOT x0 AND NOT x1 AND x2)
    qc.x(x[0])
    qc.x(x[1])
    qc.ccx(x[0], x[1], a[0])
    qc.ccx(a[0], x[2], a[3])
    qc.ccx(x[0], x[1], a[0])
    qc.x(x[0])
    qc.x(x[1])
    
    # Clause 4: (x0 OR NOT x1 OR NOT x2) -> negation: (NOT x0 AND x1 AND x2)
    qc.x(x[0])
    qc.ccx(x[0], x[1], a[0])
    qc.ccx(a[0], x[2], a[4])
    qc.ccx(x[0], x[1], a[0])
    qc.x(x[0])
    
    # Apply phase if all clause negations are 0 (all clauses satisfied)
    # Flip to convert 0→1, compute AND, apply Z, uncompute
    qc.x(a[1])
    qc.x(a[2])
    qc.x(a[3])
    qc.x(a[4])
    
    qc.ccx(a[1], a[2], a[0])
    qc.ccx(a[0], a[3], a[1])
    qc.ccx(a[1], a[4], a[0])
    qc.z(a[0])
    
    qc.ccx(a[1], a[4], a[0])
    qc.ccx(a[0], a[3], a[1])
    qc.ccx(a[1], a[2], a[0])
    
    qc.x(a[1])
    qc.x(a[2])
    qc.x(a[3])
    qc.x(a[4])
    
    # Uncompute clause negations in reverse order
    qc.x(x[0])
    qc.ccx(x[0], x[1], a[0])
    qc.ccx(a[0], x[2], a[4])
    qc.ccx(x[0], x[1], a[0])
    qc.x(x[0])
    
    qc.x(x[0])
    qc.x(x[1])
    qc.ccx(x[0], x[1], a[0])
    qc.ccx(a[0], x[2], a[3])
    qc.ccx(x[0], x[1], a[0])
    qc.x(x[0])
    qc.x(x[1])
    
    qc.x(x[0])
    qc.x(x[1])
    qc.x(x[2])
    qc.ccx(x[0], x[1], a[0])
    qc.ccx(a[0], x[2], a[2])
    qc.ccx(x[0], x[1], a[0])
    qc.x(x[0])
    qc.x(x[1])
    qc.x(x[2])
    
    qc.ccx(x[0], x[1], a[0])
    qc.ccx(a[0], x[2], a[1])
    qc.ccx(x[0], x[1], a[0])
