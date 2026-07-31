from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    # 3-SAT clauses: each is a list of (variable_index, is_positive)
    clauses = [
        [(0, True), (1, False), (5, True)],      # (x0 OR NOT x1 OR x5)
        [(2, False), (3, False), (4, True)],     # (NOT x2 OR NOT x3 OR x4)
        [(1, False), (4, True), (5, True)],      # (NOT x1 OR x4 OR x5)
        [(2, True), (4, True), (5, True)],       # (x2 OR x4 OR x5)
        [(0, False), (3, False), (5, True)],     # (NOT x0 OR NOT x3 OR x5)
        [(0, False), (2, True), (6, False)],     # (NOT x0 OR x2 OR NOT x6)
        [(0, False), (2, False), (5, True)],     # (NOT x0 OR NOT x2 OR x5)
        [(1, True), (3, True), (4, False)],      # (x1 OR x3 OR NOT x4)
        [(3, True), (4, True), (5, True)],       # (x3 OR x4 OR x5)
        [(2, True), (4, True), (6, False)],      # (x2 OR x4 OR NOT x6)
        [(2, True), (3, False), (6, True)],      # (x2 OR NOT x3 OR x6)
    ]
    
    # Ancilla allocation
    clause_result = ancilla_qubits[0]
    temp_not = ancilla_qubits[1:4]       # 3 ancillas for NOT terms in clause
    solution = ancilla_qubits[4]         # Accumulates AND of all clauses
    temp_and = ancilla_qubits[5]         # Helper for AND operation
    temp_work = ancilla_qubits[6]        # Helper for 3-controlled gates
    
    # COMPUTE PHASE
    qc.x(solution)  # Initialize solution to |1>
    
    for clause in clauses:
        # Compute current clause into clause_result
        qc.x(clause_result)  # Initialize to 1
        
        # Compute the FALSE condition: when all terms are false
        # For each term, compute ancilla that's 1 iff term is false
        for term_idx, (var_idx, is_positive) in enumerate(clause):
            if is_positive:
                # Positive term (x_i): false when x_i = 0
                qc.x(temp_not[term_idx])  # Initialize to 1
                qc.cx(problem_qubits[var_idx], temp_not[term_idx])  # Flip if x_i = 1
            else:
                # Negative term (NOT x_i): false when x_i = 1
                qc.cx(problem_qubits[var_idx], temp_not[term_idx])
        
        # Detect FALSE condition using multi-controlled X
        qc.ccx(temp_not[0], temp_not[1], temp_work)
        qc.ccx(temp_work, temp_not[2], clause_result)  # Flip if all NOT terms are 1
        qc.ccx(temp_not[0], temp_not[1], temp_work)    # Uncompute temp_work
        
        # Uncompute NOT terms
        for term_idx, (var_idx, is_positive) in enumerate(clause):
            if is_positive:
                qc.cx(problem_qubits[var_idx], temp_not[term_idx])
                qc.x(temp_not[term_idx])
            else:
                qc.cx(problem_qubits[var_idx], temp_not[term_idx])
        
        # AND clause_result into solution: solution = solution AND clause_result
        # Using: solution' = solution XOR (solution AND NOT clause_result)
        qc.x(clause_result)  # Flip to NOT clause_result
        qc.ccx(solution, clause_result, temp_and)  # temp_and = solution AND NOT clause
        qc.cx(temp_and, solution)  # solution XOR temp_and
        qc.x(clause_result)  # Flip back
        
        # Uncompute clause_result back to |0>
        qc.x(clause_result)
    
    # PHASE ORACLE: apply -1 phase iff all clauses satisfied (solution = 1)
    qc.z(solution)
    
    # UNCOMPUTE PHASE (reverse order of compute)
    for clause in reversed(clauses):
        # Re-compute clause_result
        qc.x(clause_result)
        
        for term_idx, (var_idx, is_positive) in enumerate(clause):
            if is_positive:
                qc.x(temp_not[term_idx])
                qc.cx(problem_qubits[var_idx], temp_not[term_idx])
            else:
                qc.cx(problem_qubits[var_idx], temp_not[term_idx])
        
        qc.ccx(temp_not[0], temp_not[1], temp_work)
        qc.ccx(temp_work, temp_not[2], clause_result)
        qc.ccx(temp_not[0], temp_not[1], temp_work)
        
        for term_idx, (var_idx, is_positive) in enumerate(clause):
            if is_positive:
                qc.cx(problem_qubits[var_idx], temp_not[term_idx])
                qc.x(temp_not[term_idx])
            else:
                qc.cx(problem_qubits[var_idx], temp_not[term_idx])
        
        # Uncompute AND (reverse of forward)
        qc.x(clause_result)
        qc.cx(temp_and, solution)
        qc.ccx(solution, clause_result, temp_and)
        qc.x(clause_result)
        
        # Uncompute clause_result
        qc.x(clause_result)
    
    # Uncompute solution back to |0>
    qc.x(solution)
