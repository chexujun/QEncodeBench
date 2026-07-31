from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    x = problem_qubits  # x[0] through x[5]
    a = ancilla_qubits  # a[0:7] for clauses, a[7] for temporary
    
    # Compute negation of each clause into a[0:7]
    # Clause 0: NOT(x1 AND x3 AND x5)
    qc.ccx(x[1], x[3], a[7])
    qc.ccx(x[5], a[7], a[0])
    qc.ccx(x[1], x[3], a[7])
    
    # Clause 1: NOT(x0 AND x1 AND NOT x2)
    qc.ccx(x[0], x[1], a[7])
    qc.x(x[2])
    qc.ccx(x[2], a[7], a[1])
    qc.x(x[2])
    qc.ccx(x[0], x[1], a[7])
    
    # Clause 2: NOT(x1 AND x2 AND x5)
    qc.ccx(x[1], x[2], a[7])
    qc.ccx(x[5], a[7], a[2])
    qc.ccx(x[1], x[2], a[7])
    
    # Clause 3: NOT(x1 AND NOT x4 AND x5)
    qc.ccx(x[1], x[5], a[7])
    qc.x(x[4])
    qc.ccx(x[4], a[7], a[3])
    qc.x(x[4])
    qc.ccx(x[1], x[5], a[7])
    
    # Clause 4: NOT(x0 AND x1 AND NOT x5)
    qc.ccx(x[0], x[1], a[7])
    qc.x(x[5])
    qc.ccx(x[5], a[7], a[4])
    qc.x(x[5])
    qc.ccx(x[0], x[1], a[7])
    
    # Clause 5: NOT(NOT x2 AND x4 AND NOT x5)
    qc.x(x[2])
    qc.ccx(x[2], x[4], a[7])
    qc.x(x[2])
    qc.x(x[5])
    qc.ccx(x[5], a[7], a[5])
    qc.x(x[5])
    qc.x(x[2])
    qc.ccx(x[2], x[4], a[7])
    qc.x(x[2])
    
    # Clause 6: NOT(x2 AND x3 AND x4)
    qc.ccx(x[2], x[3], a[7])
    qc.ccx(x[4], a[7], a[6])
    qc.ccx(x[2], x[3], a[7])
    
    # Flip to convert negations to clause values
    for i in range(7):
        qc.x(a[i])
    
    # Compute AND of all clauses using serial Toffoli chain
    qc.ccx(a[0], a[1], a[7])
    qc.ccx(a[2], a[7], a[0])
    qc.ccx(a[3], a[0], a[7])
    qc.ccx(a[4], a[7], a[1])
    qc.ccx(a[5], a[1], a[7])
    qc.ccx(a[6], a[7], a[2])
    
    # Apply phase
    qc.z(a[2])
    
    # Uncompute AND
    qc.ccx(a[6], a[7], a[2])
    qc.ccx(a[5], a[1], a[7])
    qc.ccx(a[4], a[7], a[1])
    qc.ccx(a[3], a[0], a[7])
    qc.ccx(a[2], a[7], a[0])
    qc.ccx(a[0], a[1], a[7])
    
    # Flip back to negations
    for i in range(7):
        qc.x(a[i])
    
    # Uncompute clause negations
    qc.ccx(x[1], x[3], a[7])
    qc.ccx(x[5], a[7], a[0])
    qc.ccx(x[1], x[3], a[7])
    
    qc.ccx(x[0], x[1], a[7])
    qc.x(x[2])
    qc.ccx(x[2], a[7], a[1])
    qc.x(x[2])
    qc.ccx(x[0], x[1], a[7])
    
    qc.ccx(x[1], x[2], a[7])
    qc.ccx(x[5], a[7], a[2])
    qc.ccx(x[1], x[2], a[7])
    
    qc.ccx(x[1], x[5], a[7])
    qc.x(x[4])
    qc.ccx(x[4], a[7], a[3])
    qc.x(x[4])
    qc.ccx(x[1], x[5], a[7])
    
    qc.ccx(x[0], x[1], a[7])
    qc.x(x[5])
    qc.ccx(x[5], a[7], a[4])
    qc.x(x[5])
    qc.ccx(x[0], x[1], a[7])
    
    qc.x(x[2])
    qc.ccx(x[2], x[4], a[7])
    qc.x(x[2])
    qc.x(x[5])
    qc.ccx(x[5], a[7], a[5])
    qc.x(x[5])
    qc.x(x[2])
    qc.ccx(x[2], x[4], a[7])
    qc.x(x[2])
    
    qc.ccx(x[2], x[3], a[7])
    qc.ccx(x[4], a[7], a[6])
    qc.ccx(x[2], x[3], a[7])
