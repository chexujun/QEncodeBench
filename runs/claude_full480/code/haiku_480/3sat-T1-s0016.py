from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x = problem_qubits
    a = ancilla_qubits
    
    def compute_or_clause(clause_bit, var_indices, negations):
        """Compute OR of 3 literals into clause_bit.
        Evaluates (L1 OR L2 OR L3) = NOT(NOT L1 AND NOT L2 AND NOT L3)"""
        temp = a[5]
        
        qc.x(clause_bit)
        
        # Apply X to variables that appear negated
        for idx, var_idx in enumerate(var_indices):
            if negations[idx]:
                qc.x(x[var_idx])
        
        # Compute AND of three (possibly flipped) qubits into temp, then into clause_bit
        qc.ccx(x[var_indices[0]], x[var_indices[1]], temp)
        qc.ccx(temp, x[var_indices[2]], clause_bit)
        qc.ccx(x[var_indices[0]], x[var_indices[1]], temp)
        
        # Undo X gates
        for idx, var_idx in enumerate(var_indices):
            if negations[idx]:
                qc.x(x[var_idx])
    
    clause_specs = [
        (a[0], [0, 1, 2], [True, False, False]),   # (NOT x0 OR x1 OR x2)
        (a[1], [0, 1, 2], [False, True, False]),   # (x0 OR NOT x1 OR x2)
        (a[2], [0, 1, 2], [False, False, False]),  # (x0 OR x1 OR x2)
        (a[3], [0, 1, 2], [True, False, True]),    # (NOT x0 OR x1 OR NOT x2)
        (a[4], [0, 1, 2], [False, False, True]),   # (x0 OR x1 OR NOT x2)
    ]
    
    # Compute all clause satisfaction bits
    for clause_bit, var_indices, negations in clause_specs:
        compute_or_clause(clause_bit, var_indices, negations)
    
    # Compute AND of all clauses into a[5]
    temp = a[5]
    qc.x(temp)  # temp = 1
    
    for i in range(5):
        qc.x(a[i])
        qc.ccx(temp, a[i], temp)  # temp AND= a[i]
        qc.x(a[i])
    
    # Apply phase -1 if all clauses satisfied
    qc.z(temp)
    
    # Uncompute AND
    for i in range(5):
        qc.x(a[i])
        qc.ccx(temp, a[i], temp)
        qc.x(a[i])
    
    # Uncompute clauses in reverse
    for clause_bit, var_indices, negations in reversed(clause_specs):
        compute_or_clause(clause_bit, var_indices, negations)
