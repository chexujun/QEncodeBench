from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    
    clauses = [
        [(0, True), (4, True), (5, True)],    # NOT x0 OR NOT x4 OR NOT x5
        [(2, True), (3, False), (4, False)],  # NOT x2 OR x3 OR x4
        [(1, False), (3, True), (5, True)],   # x1 OR NOT x3 OR NOT x5
        [(0, True), (1, False), (2, False)],  # NOT x0 OR x1 OR x2
        [(1, True), (3, True), (4, True)],    # NOT x1 OR NOT x3 OR NOT x4
        [(0, True), (2, False), (4, True)],   # NOT x0 OR x2 OR NOT x4
        [(1, True), (3, False), (4, True)],   # NOT x1 OR x3 OR NOT x4
        [(0, True), (1, False), (3, False)],  # NOT x0 OR x1 OR x3
        [(0, True), (3, False), (5, False)],  # NOT x0 OR x3 OR x5
        [(1, False), (4, False), (5, False)], # x1 OR x4 OR x5
    ]
    
    clause_results = ancilla_qubits[:10]
    formula_result = ancilla_qubits[10]
    
    # Compute each clause: result is 1 iff clause is satisfied
    for i, clause in enumerate(clauses):
        compute_or_clause(qc, problem_qubits, clause, clause_results[i])
    
    # Compute AND of all clauses into formula_result
    qc.ccx(clause_results[0], clause_results[1], formula_result)
    for i in range(2, 10):
        qc.ccx(formula_result, clause_results[i], formula_result)
    
    # Apply Z phase (phase -1 iff all clauses satisfied)
    qc.z(formula_result)
    
    # Uncompute AND (reverse order)
    for i in range(9, 1, -1):
        qc.ccx(formula_result, clause_results[i], formula_result)
    qc.ccx(clause_results[0], clause_results[1], formula_result)
    
    # Uncompute clauses (reverse order)
    for i in range(9, -1, -1):
        uncompute_or_clause(qc, problem_qubits, clauses[i], clause_results[i])


def compute_or_clause(qc, problem_qubits, clause, result_qubit):
    # Compute (l1 OR l2 OR l3) into result_qubit (initially |0>)
    # Use: (l1 OR l2 OR l3) = NOT(NOT l1 AND NOT l2 AND NOT l3)
    
    # Flip problem qubits for non-negated literals
    # This makes each control activate when the literal is false
    flipped_vars = []
    for var, is_neg in clause:
        if not is_neg:
            qc.x(problem_qubits[var])
            flipped_vars.append(var)
    
    # Multi-controlled-X: sets result=1 iff all literals are false (clause is false)
    control_qubits = [problem_qubits[var] for var, _ in clause]
    qc.mcx(control_qubits, result_qubit)
    
    # Restore flipped qubits
    for var in flipped_vars:
        qc.x(problem_qubits[var])
    
    # Negate: now result=1 iff clause is true
    qc.x(result_qubit)


def uncompute_or_clause(qc, problem_qubits, clause, result_qubit):
    # Reverse of compute_or_clause
    qc.x(result_qubit)
    
    flipped_vars = []
    for var, is_neg in clause:
        if not is_neg:
            qc.x(problem_qubits[var])
            flipped_vars.append(var)
    
    control_qubits = [problem_qubits[var] for var, _ in clause]
    qc.mcx(control_qubits, result_qubit)
    
    for var in flipped_vars:
        qc.x(problem_qubits[var])
