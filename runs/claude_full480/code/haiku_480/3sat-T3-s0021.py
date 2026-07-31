from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x = problem_qubits
    c = ancilla_qubits[:7]  # clause ancillas
    h = ancilla_qubits[7]   # overall AND result
    
    # Compute NOT(clause_i) into c[i] for each clause
    # Clause 1: (x2 OR x3 OR x4) -> NOT = (NOT x2) AND (NOT x3) AND (NOT x4)
    qc.x(c[0])
    qc.ccx(x[2], x[3], c[0])
    qc.cx(x[4], c[0])
    qc.ccx(x[2], x[3], c[0])
    qc.x(c[0])
    
    # Clause 2: (x2 OR x4 OR x5) -> NOT = (NOT x2) AND (NOT x4) AND (NOT x5)
    qc.x(c[1])
    qc.ccx(x[2], x[4], c[1])
    qc.cx(x[5], c[1])
    qc.ccx(x[2], x[4], c[1])
    qc.x(c[1])
    
    # Clause 3: (NOT x0 OR x1 OR x5) -> NOT = (x0 AND NOT x1 AND NOT x5)
    qc.x(c[2])
    qc.x(x[1])
    qc.x(x[5])
    qc.ccx(x[0], x[1], c[2])
    qc.cx(x[5], c[2])
    qc.ccx(x[0], x[1], c[2])
    qc.x(x[1])
    qc.x(x[5])
    qc.x(c[2])
    
    # Clause 4: (x0 OR NOT x3 OR x5) -> NOT = (NOT x0 AND x3 AND NOT x5)
    qc.x(c[3])
    qc.x(x[0])
    qc.x(x[5])
    qc.ccx(x[0], x[3], c[3])
    qc.cx(x[5], c[3])
    qc.ccx(x[0], x[3], c[3])
    qc.x(x[0])
    qc.x(x[5])
    qc.x(c[3])
    
    # Clause 5: (NOT x0 OR NOT x3 OR NOT x4) -> NOT = (x0 AND x3 AND x4)
    qc.x(c[4])
    qc.ccx(x[0], x[3], c[4])
    qc.cx(x[4], c[4])
    qc.ccx(x[0], x[3], c[4])
    qc.x(c[4])
    
    # Clause 6: (NOT x0 OR NOT x1 OR x2) -> NOT = (x0 AND x1 AND NOT x2)
    qc.x(c[5])
    qc.x(x[2])
    qc.ccx(x[0], x[1], c[5])
    qc.cx(x[2], c[5])
    qc.ccx(x[0], x[1], c[5])
    qc.x(x[2])
    qc.x(c[5])
    
    # Clause 7: (NOT x0 OR x3 OR x5) -> NOT = (x0 AND NOT x3 AND NOT x5)
    qc.x(c[6])
    qc.x(x[3])
    qc.x(x[5])
    qc.ccx(x[0], x[3], c[6])
    qc.cx(x[5], c[6])
    qc.ccx(x[0], x[3], c[6])
    qc.x(x[3])
    qc.x(x[5])
    qc.x(c[6])
    
    # Compute h = 1 iff all c[i] = 0 (all clauses satisfied)
    # Use mcx with inverted controls
    for ci in c:
        qc.x(ci)
    qc.mcx(c, h)
    for ci in c:
        qc.x(ci)
    
    # Apply phase -1 when all clauses are satisfied
    qc.z(h)
    
    # Uncompute h
    for ci in c:
        qc.x(ci)
    qc.mcx(c, h)
    for ci in c:
        qc.x(ci)
    
    # Uncompute clause ancillas in reverse order
    # Clause 7
    qc.x(c[6])
    qc.x(x[3])
    qc.x(x[5])
    qc.ccx(x[0], x[3], c[6])
    qc.cx(x[5], c[6])
    qc.ccx(x[0], x[3], c[6])
    qc.x(x[3])
    qc.x(x[5])
    
    # Clause 6
    qc.x(c[5])
    qc.x(x[2])
    qc.ccx(x[0], x[1], c[5])
    qc.cx(x[2], c[5])
    qc.ccx(x[0], x[1], c[5])
    qc.x(x[2])
    
    # Clause 5
    qc.x(c[4])
    qc.ccx(x[0], x[3], c[4])
    qc.cx(x[4], c[4])
    qc.ccx(x[0], x[3], c[4])
    
    # Clause 4
    qc.x(c[3])
    qc.x(x[0])
    qc.x(x[5])
    qc.ccx(x[0], x[3], c[3])
    qc.cx(x[5], c[3])
    qc.ccx(x[0], x[3], c[3])
    qc.x(x[0])
    qc.x(x[5])
    
    # Clause 3
    qc.x(c[2])
    qc.x(x[1])
    qc.x(x[5])
    qc.ccx(x[0], x[1], c[2])
    qc.cx(x[5], c[2])
    qc.ccx(x[0], x[1], c[2])
    qc.x(x[1])
    qc.x(x[5])
    
    # Clause 2
    qc.x(c[1])
    qc.ccx(x[2], x[4], c[1])
    qc.cx(x[5], c[1])
    qc.ccx(x[2], x[4], c[1])
    
    # Clause 1
    qc.x(c[0])
    qc.ccx(x[2], x[3], c[0])
    qc.cx(x[4], c[0])
    qc.ccx(x[2], x[3], c[0])
