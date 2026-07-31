from qiskit import QuantumCircuit

def build_oracle(qc, problem_qubits, ancilla_qubits):
    x0, x1, x2 = problem_qubits
    a0, a1, a2, a3, a4, a5 = ancilla_qubits
    
    # Clause unsatisfaction conditions (when clause evaluates to FALSE):
    # Clause 1: (NOT x0 OR x1 OR NOT x2) FALSE iff (x0=1 AND x1=0 AND x2=1)
    # Clause 2: (NOT x0 OR NOT x1 OR NOT x2) FALSE iff (x0=1 AND x1=1 AND x2=1)
    # Clause 3: (NOT x0 OR NOT x1 OR x2) FALSE iff (x0=1 AND x1=1 AND x2=0)
    # Clause 4: (x0 OR NOT x1 OR x2) FALSE iff (x0=0 AND x1=1 AND x2=0)
    # Clause 5: (x0 OR x1 OR x2) FALSE iff (x0=0 AND x1=0 AND x2=0)
    
    # Compute each clause unsatisfaction condition into corresponding ancilla
    # Clause 1: x0 AND NOT x1 AND x2
    qc.x(x1)
    qc.mcx([x0, x1, x2], a0)
    qc.x(x1)
    
    # Clause 2: x0 AND x1 AND x2
    qc.mcx([x0, x1, x2], a1)
    
    # Clause 3: x0 AND x1 AND NOT x2
    qc.x(x2)
    qc.mcx([x0, x1, x2], a2)
    qc.x(x2)
    
    # Clause 4: NOT x0 AND x1 AND NOT x2
    qc.x(x0)
    qc.x(x2)
    qc.mcx([x0, x1, x2], a3)
    qc.x(x2)
    qc.x(x0)
    
    # Clause 5: NOT x0 AND NOT x1 AND NOT x2
    qc.x(x0)
    qc.x(x1)
    qc.x(x2)
    qc.mcx([x0, x1, x2], a4)
    qc.x(x2)
    qc.x(x1)
    qc.x(x0)
    
    # Compute OR of all unsatisfaction flags into a5
    # a5 = 1 if any clause is unsatisfied (formula is unsatisfied)
    # a5 = 0 if all clauses are satisfied (formula is satisfied)
    # Use: a5 = NOT(NOT a0 AND NOT a1 AND NOT a2 AND NOT a3 AND NOT a4)
    
    qc.x(a5)  # initialize a5 to 1
    qc.x(a0)
    qc.x(a1)
    qc.x(a2)
    qc.x(a3)
    qc.x(a4)
    qc.mcx([a0, a1, a2, a3, a4], a5)  # a5 XOR= (NOT a0 AND ... AND NOT a4)
    qc.x(a4)
    qc.x(a3)
    qc.x(a2)
    qc.x(a1)
    qc.x(a0)
    
    # Now a5 = 0 iff formula is satisfied, a5 = 1 iff formula is unsatisfied
    # Apply phase -1 when formula is satisfied (a5 = 0)
    qc.x(a5)  # flip so a5 = 1 when formula is satisfied
    qc.z(a5)  # apply phase -1 to |1> state
    qc.x(a5)  # flip back to original value
    
    # Uncompute: reverse the OR computation
    qc.x(a0)
    qc.x(a1)
    qc.x(a2)
    qc.x(a3)
    qc.x(a4)
    qc.mcx([a0, a1, a2, a3, a4], a5)
    qc.x(a4)
    qc.x(a3)
    qc.x(a2)
    qc.x(a1)
    qc.x(a0)
    qc.x(a5)
    
    # Uncompute clause conditions in reverse order
    # Clause 5
    qc.x(x0)
    qc.x(x1)
    qc.x(x2)
    qc.mcx([x0, x1, x2], a4)
    qc.x(x2)
    qc.x(x1)
    qc.x(x0)
    
    # Clause 4
    qc.x(x0)
    qc.x(x2)
    qc.mcx([x0, x1, x2], a3)
    qc.x(x2)
    qc.x(x0)
    
    # Clause 3
    qc.x(x2)
    qc.mcx([x0, x1, x2], a2)
    qc.x(x2)
    
    # Clause 2
    qc.mcx([x0, x1, x2], a1)
    
    # Clause 1
    qc.x(x1)
    qc.mcx([x0, x1, x2], a0)
    qc.x(x1)
