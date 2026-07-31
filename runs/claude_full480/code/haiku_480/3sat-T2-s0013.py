from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    """
    3-SAT oracle: applies phase -1 to basis states satisfying all 6 clauses.
    
    Clauses:
      0. (x0 OR x2 OR NOT x3)
      1. (NOT x1 OR x2 OR x4)
      2. (NOT x0 OR x1 OR NOT x4)
      3. (x1 OR NOT x2 OR NOT x4)
      4. (NOT x2 OR NOT x3 OR x4)
      5. (NOT x0 OR x1 OR x2)
    """
    x = problem_qubits
    a = ancilla_qubits
    
    # Compute failure condition for each clause into a[0:6]
    # Clause i fails iff all its literals are false
    
    # Clause 0: (x0 OR x2 OR NOT x3) fails iff (NOT x0) AND (NOT x2) AND x3
    qc.x(x[0])
    qc.x(x[2])
    qc.mcx([x[0], x[2], x[3]], a[0])
    qc.x(x[2])
    qc.x(x[0])
    
    # Clause 1: (NOT x1 OR x2 OR x4) fails iff x1 AND (NOT x2) AND (NOT x4)
    qc.x(x[2])
    qc.x(x[4])
    qc.mcx([x[1], x[2], x[4]], a[1])
    qc.x(x[4])
    qc.x(x[2])
    
    # Clause 2: (NOT x0 OR x1 OR NOT x4) fails iff x0 AND (NOT x1) AND x4
    qc.x(x[1])
    qc.mcx([x[0], x[1], x[4]], a[2])
    qc.x(x[1])
    
    # Clause 3: (x1 OR NOT x2 OR NOT x4) fails iff (NOT x1) AND x2 AND x4
    qc.x(x[1])
    qc.mcx([x[1], x[2], x[4]], a[3])
    qc.x(x[1])
    
    # Clause 4: (NOT x2 OR NOT x3 OR x4) fails iff x2 AND x3 AND (NOT x4)
    qc.x(x[4])
    qc.mcx([x[2], x[3], x[4]], a[4])
    qc.x(x[4])
    
    # Clause 5: (NOT x0 OR x1 OR x2) fails iff x0 AND (NOT x1) AND (NOT x2)
    qc.x(x[1])
    qc.x(x[2])
    qc.mcx([x[0], x[1], x[2]], a[5])
    qc.x(x[2])
    qc.x(x[1])
    
    # Compute: all_satisfied = (NOT a[0]) AND (NOT a[1]) AND ... AND (NOT a[5])
    # Start with a[6] = 1, then for each failure ancilla a[i]:
    #   a[6] := a[6] AND (NOT a[i])
    # Using CCX identity: if a[6] = 1, then CCX(a[i], a[6], a[6]) gives a[6] := NOT a[i]
    # If a[6] = 0, then a[6] stays 0, realizing the AND
    
    qc.x(a[6])  # Initialize a[6] = 1
    
    # Accumulate: a[6] = (NOT a[0]) AND (NOT a[1]) AND ... AND (NOT a[5])
    for i in range(6):
        qc.ccx(a[i], a[6], a[6])
    
    # Apply phase -1 if all clauses satisfied
    qc.z(a[6])
    
    # Uncompute: restore all ancillas to |0>
    for i in range(6):
        qc.ccx(a[i], a[6], a[6])
    
    qc.x(a[6])  # Restore a[6] = 0
    
    # Uncompute clause failure conditions (reverse order)
    qc.x(x[1])
    qc.x(x[2])
    qc.mcx([x[0], x[1], x[2]], a[5])
    qc.x(x[2])
    qc.x(x[1])
    
    qc.x(x[4])
    qc.mcx([x[2], x[3], x[4]], a[4])
    qc.x(x[4])
    
    qc.x(x[1])
    qc.mcx([x[1], x[2], x[4]], a[3])
    qc.x(x[1])
    
    qc.x(x[1])
    qc.mcx([x[0], x[1], x[4]], a[2])
    qc.x(x[1])
    
    qc.x(x[2])
    qc.x(x[4])
    qc.mcx([x[1], x[2], x[4]], a[1])
    qc.x(x[4])
    qc.x(x[2])
    
    qc.x(x[0])
    qc.x(x[2])
    qc.mcx([x[0], x[2], x[3]], a[0])
    qc.x(x[2])
    qc.x(x[0])
