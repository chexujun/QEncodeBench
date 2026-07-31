from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    
    def compute_or_clause(qc, qubits, is_negated, result_q, temp_q):
        """
        Compute OR of (NOT qubits[i] if is_negated[i], else qubits[i])
        into result_q using the formula: OR = NOT(AND(NOT inputs)).
        Both result_q and temp_q must start at |0>.
        """
        # Convert is_negated to negations needed for the AND formula
        negations_for_formula = [not neg for neg in is_negated]
        a, b, c = qubits[0], qubits[1], qubits[2]
        neg_a, neg_b, neg_c = negations_for_formula
        
        # Apply X gates to compute NOT of each literal
        if neg_a:
            qc.x(a)
        if neg_b:
            qc.x(b)
        if neg_c:
            qc.x(c)
        
        # Compute AND(a, b, c) into result_q using Toffoli gates
        qc.ccx(a, b, result_q)      # result = a AND b
        qc.ccx(c, result_q, temp_q) # temp = c AND result
        qc.cx(temp_q, result_q)     # result XOR= temp to extract AND
        qc.ccx(c, result_q, temp_q) # uncompute temp
        
        # Negate the result: NOT(AND(...)) = OR(...)
        qc.x(result_q)
        
        # Restore all input qubits
        if neg_c:
            qc.x(c)
        if neg_b:
            qc.x(b)
        if neg_a:
            qc.x(a)
    
    x = problem_qubits
    a = ancilla_qubits
    
    # Compute each clause into ancilla qubits
    # Clause 1: (x0 OR x1 OR x3)
    compute_or_clause(qc, [x[0], x[1], x[3]], [False, False, False], a[0], a[4])
    
    # Clause 2: (NOT x0 OR x1 OR NOT x2)
    compute_or_clause(qc, [x[0], x[1], x[2]], [True, False, True], a[1], a[4])
    
    # Clause 3: (NOT x0 OR x2 OR NOT x3)
    compute_or_clause(qc, [x[0], x[2], x[3]], [True, False, True], a[2], a[4])
    
    # Clause 4: (NOT x1 OR NOT x2 OR x3)
    compute_or_clause(qc, [x[1], x[2], x[3]], [True, True, False], a[3], a[4])
    
    # AND all four clause results: mark if all are satisfied
    qc.mcx([a[0], a[1], a[2], a[3]], a[4])
    
    # Apply phase flip for satisfying assignments
    qc.z(a[4])
    
    # Uncompute: reverse all operations to restore ancillas to |0>
    qc.mcx([a[0], a[1], a[2], a[3]], a[4])
    
    # Uncompute clauses in reverse order
    compute_or_clause(qc, [x[1], x[2], x[3]], [True, True, False], a[3], a[4])
    compute_or_clause(qc, [x[0], x[2], x[3]], [True, False, True], a[2], a[4])
    compute_or_clause(qc, [x[0], x[1], x[2]], [True, False, True], a[1], a[4])
    compute_or_clause(qc, [x[0], x[1], x[3]], [False, False, False], a[0], a[4])
