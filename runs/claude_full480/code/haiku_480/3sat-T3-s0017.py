from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x = problem_qubits
    a = ancilla_qubits
    
    # Compute each clause into a[0:7]
    # Clause 1: (NOT x3 OR NOT x5 OR NOT x6) = NOT(x3 AND x5 AND x6)
    qc.x(a[0])
    qc.ccx(x[5], x[6], a[7])
    qc.ccx(x[3], a[7], a[0])
    qc.ccx(x[5], x[6], a[7])
    
    # Clause 2: (NOT x2 OR NOT x6 OR NOT x7) = NOT(x2 AND x6 AND x7)
    qc.x(a[1])
    qc.ccx(x[6], x[7], a[7])
    qc.ccx(x[2], a[7], a[1])
    qc.ccx(x[6], x[7], a[7])
    
    # Clause 3: (x0 OR x3 OR NOT x6) = NOT((NOT x0) AND (NOT x3) AND x6)
    qc.x(a[2])
    qc.x(x[0])
    qc.x(x[3])
    qc.ccx(x[0], x[3], a[7])
    qc.ccx(a[7], x[6], a[2])
    qc.ccx(x[0], x[3], a[7])
    qc.x(x[3])
    qc.x(x[0])
    
    # Clause 4: (NOT x1 OR x6 OR x7) = NOT((NOT NOT x1) AND (NOT x6) AND (NOT x7))
    #                                 = NOT(x1 AND (NOT x6) AND (NOT x7))
    qc.x(a[3])
    qc.x(x[6])
    qc.x(x[7])
    qc.ccx(x[6], x[7], a[7])
    qc.ccx(x[1], a[7], a[3])
    qc.ccx(x[6], x[7], a[7])
    qc.x(x[7])
    qc.x(x[6])
    
    # Clause 5: (NOT x2 OR NOT x4 OR x6) = NOT((NOT NOT x2) AND (NOT NOT x4) AND (NOT x6))
    #                                     = NOT(x2 AND x4 AND (NOT x6))
    qc.x(a[4])
    qc.x(x[6])
    qc.ccx(x[4], x[6], a[7])
    qc.ccx(x[2], a[7], a[4])
    qc.ccx(x[4], x[6], a[7])
    qc.x(x[6])
    
    # Clause 6: (x1 OR NOT x2 OR NOT x5) = NOT((NOT x1) AND x2 AND x5)
    qc.x(a[5])
    qc.x(x[1])
    qc.ccx(x[2], x[5], a[7])
    qc.ccx(x[1], a[7], a[5])
    qc.ccx(x[2], x[5], a[7])
    qc.x(x[1])
    
    # Clause 7: (NOT x3 OR x4 OR x5) = NOT((NOT NOT x3) AND (NOT x4) AND (NOT x5))
    #                                 = NOT(x3 AND (NOT x4) AND (NOT x5))
    qc.x(a[6])
    qc.x(x[4])
    qc.x(x[5])
    qc.ccx(x[4], x[5], a[7])
    qc.ccx(x[3], a[7], a[6])
    qc.ccx(x[4], x[5], a[7])
    qc.x(x[5])
    qc.x(x[4])
    
    # Compute AND of all clauses into a[7]
    qc.ccx(a[0], a[1], a[7])
    qc.ccx(a[7], a[2], a[0])
    qc.ccx(a[0], a[3], a[7])
    qc.ccx(a[7], a[4], a[1])
    qc.ccx(a[1], a[5], a[7])
    qc.ccx(a[7], a[6], a[2])
    qc.cx(a[2], a[7])
    
    # Apply phase
    qc.z(a[7])
    
    # Uncompute AND (reverse of compute)
    qc.cx(a[2], a[7])
    qc.ccx(a[7], a[6], a[2])
    qc.ccx(a[1], a[5], a[7])
    qc.ccx(a[7], a[4], a[1])
    qc.ccx(a[0], a[3], a[7])
    qc.ccx(a[7], a[2], a[0])
    qc.ccx(a[0], a[1], a[7])
    
    # Uncompute clauses (reverse order, reverse operations)
    qc.x(x[4])
    qc.x(x[5])
    qc.ccx(x[4], x[5], a[7])
    qc.ccx(x[3], a[7], a[6])
    qc.ccx(x[4], x[5], a[7])
    qc.x(x[5])
    qc.x(x[4])
    
    qc.x(x[1])
    qc.ccx(x[2], x[5], a[7])
    qc.ccx(x[1], a[7], a[5])
    qc.ccx(x[2], x[5], a[7])
    qc.x(x[1])
    
    qc.x(x[6])
    qc.ccx(x[4], x[6], a[7])
    qc.ccx(x[2], a[7], a[4])
    qc.ccx(x[4], x[6], a[7])
    qc.x(x[6])
    
    qc.x(x[6])
    qc.x(x[7])
    qc.ccx(x[6], x[7], a[7])
    qc.ccx(x[1], a[7], a[3])
    qc.ccx(x[6], x[7], a[7])
    qc.x(x[7])
    qc.x(x[6])
    
    qc.x(x[0])
    qc.x(x[3])
    qc.ccx(x[0], x[3], a[7])
    qc.ccx(a[7], x[6], a[2])
    qc.ccx(x[0], x[3], a[7])
    qc.x(x[3])
    qc.x(x[0])
    
    qc.ccx(x[6], x[7], a[7])
    qc.ccx(x[2], a[7], a[1])
    qc.ccx(x[6], x[7], a[7])
    
    qc.ccx(x[5], x[6], a[7])
    qc.ccx(x[3], a[7], a[0])
    qc.ccx(x[5], x[6], a[7])
