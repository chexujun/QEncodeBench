from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    """
    Phase oracle for 3-SAT formula:
      (NOT x0 OR NOT x2 OR x3) AND
      (NOT x0 OR x2 OR x3) AND
      (NOT x0 OR x1 OR x2) AND
      (x0 OR NOT x1 OR x2) AND
      (x1 OR NOT x2 OR x3)
    
    Applies phase -1 iff all clauses are satisfied.
    """
    x = problem_qubits  # [0, 1, 2, 3]
    a = ancilla_qubits  # [4, 5, 6, 7, 8, 9]
    
    # For each clause, compute whether it's satisfied into ancillas a[0:5]
    # Then AND them together, apply phase, and uncompute
    
    # Clause 1: (NOT x0 OR NOT x2 OR x3) = NOT(x0 AND x2 AND NOT x3)
    qc.ccx(x[0], x[2], a[5])       # a[5] = x0 AND x2
    qc.x(a[4])                      # temp for NOT x3
    qc.cx(x[3], a[4])               # a[4] = NOT x3
    qc.ccx(a[5], a[4], a[6])        # a[6] = x0 AND x2 AND NOT x3
    qc.x(a[0])                      # a[0] = 1
    qc.cx(a[6], a[0])               # a[0] = NOT(x0 AND x2 AND NOT x3)
    qc.ccx(a[5], a[4], a[6])        # uncompute a[6]
    qc.cx(x[3], a[4])               # uncompute a[4]
    qc.x(a[4])
    qc.ccx(x[0], x[2], a[5])        # uncompute a[5]
    
    # Clause 2: (NOT x0 OR x2 OR x3) = NOT(x0 AND NOT x2 AND NOT x3)
    qc.x(a[5])                      # temp for NOT x2
    qc.cx(x[2], a[5])               # a[5] = NOT x2
    qc.ccx(x[0], a[5], a[4])        # a[4] = x0 AND NOT x2
    qc.x(a[6])                      # temp for NOT x3
    qc.cx(x[3], a[6])               # a[6] = NOT x3
    qc.ccx(a[4], a[6], a[7])        # a[7] = x0 AND NOT x2 AND NOT x3
    qc.x(a[1])
    qc.cx(a[7], a[1])               # a[1] = NOT(x0 AND NOT x2 AND NOT x3)
    qc.ccx(a[4], a[6], a[7])        # uncompute a[7]
    qc.cx(x[3], a[6])
    qc.x(a[6])
    qc.ccx(x[0], a[5], a[4])        # uncompute a[4]
    qc.cx(x[2], a[5])
    qc.x(a[5])
    
    # Clause 3: (NOT x0 OR x1 OR x2) = NOT(x0 AND NOT x1 AND NOT x2)
    qc.x(a[5])
    qc.cx(x[1], a[5])               # a[5] = NOT x1
    qc.x(a[4])
    qc.cx(x[2], a[4])               # a[4] = NOT x2
    qc.ccx(x[0], a[5], a[6])        # a[6] = x0 AND NOT x1
    qc.ccx(a[6], a[4], a[7])        # a[7] = x0 AND NOT x1 AND NOT x2
    qc.x(a[2])
    qc.cx(a[7], a[2])               # a[2] = NOT(x0 AND NOT x1 AND NOT x2)
    qc.ccx(a[6], a[4], a[7])        # uncompute a[7]
    qc.ccx(x[0], a[5], a[6])        # uncompute a[6]
    qc.cx(x[2], a[4])
    qc.x(a[4])
    qc.cx(x[1], a[5])
    qc.x(a[5])
    
    # Clause 4: (x0 OR NOT x1 OR x2) = NOT(NOT x0 AND x1 AND NOT x2)
    qc.x(a[5])
    qc.cx(x[0], a[5])               # a[5] = NOT x0
    qc.x(a[4])
    qc.cx(x[2], a[4])               # a[4] = NOT x2
    qc.ccx(a[5], x[1], a[6])        # a[6] = NOT x0 AND x1
    qc.ccx(a[6], a[4], a[7])        # a[7] = NOT x0 AND x1 AND NOT x2
    qc.x(a[3])
    qc.cx(a[7], a[3])               # a[3] = NOT(NOT x0 AND x1 AND NOT x2)
    qc.ccx(a[6], a[4], a[7])        # uncompute a[7]
    qc.ccx(a[5], x[1], a[6])        # uncompute a[6]
    qc.cx(x[2], a[4])
    qc.x(a[4])
    qc.cx(x[0], a[5])
    qc.x(a[5])
    
    # Clause 5: (x1 OR NOT x2 OR x3) = NOT(NOT x1 AND x2 AND NOT x3)
    qc.x(a[5])
    qc.cx(x[1], a[5])               # a[5] = NOT x1
    qc.x(a[4])
    qc.cx(x[3], a[4])               # a[4] = NOT x3
    qc.ccx(a[5], x[2], a[6])        # a[6] = NOT x1 AND x2
    qc.ccx(a[6], a[4], a[7])        # a[7] = NOT x1 AND x2 AND NOT x3
    qc.x(a[8])
    qc.cx(a[7], a[8])               # a[8] = NOT(NOT x1 AND x2 AND NOT x3)
    qc.ccx(a[6], a[4], a[7])        # uncompute a[7]
    qc.ccx(a[5], x[2], a[6])        # uncompute a[6]
    qc.cx(x[3], a[4])
    qc.x(a[4])
    qc.cx(x[1], a[5])
    qc.x(a[5])
    
    # AND all clause results: a[0], a[1], a[2], a[3], a[8]
    qc.ccx(a[0], a[1], a[4])        # a[4] = a[0] AND a[1]
    qc.ccx(a[4], a[2], a[5])        # a[5] = a[4] AND a[2]
    qc.ccx(a[5], a[3], a[6])        # a[6] = a[5] AND a[3]
    qc.ccx(a[6], a[8], a[7])        # a[7] = a[6] AND a[8]
    
    # Apply phase if all clauses satisfied
    qc.z(a[7])
    
    # Uncompute AND chain
    qc.ccx(a[6], a[8], a[7])
    qc.ccx(a[5], a[3], a[6])
    qc.ccx(a[4], a[2], a[5])
    qc.ccx(a[0], a[1], a[4])
