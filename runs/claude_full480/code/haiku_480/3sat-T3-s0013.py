from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    def compute_clause_satisfaction(qc, problem_qubits, clause, result_ancilla):
        # Flip qubits for negated literals in the clause
        for idx, is_negated in clause:
            if is_negated:
                qc.x(problem_qubits[idx])
        
        # Compute AND of the three literals, store result
        # (OR = NOT(AND of negations), handled below)
        qc.mcx([problem_qubits[idx] for idx, _ in clause], result_ancilla)
        
        # Negate to convert AND to OR
        qc.x(result_ancilla)
        
        # Restore qubits to original state
        for idx, is_negated in clause:
            if is_negated:
                qc.x(problem_qubits[idx])

    def uncompute_clause_satisfaction(qc, problem_qubits, clause, result_ancilla):
        # Mirror of compute: restore clause result ancilla to |0>
        for idx, is_negated in clause:
            if is_negated:
                qc.x(problem_qubits[idx])
        
        qc.x(result_ancilla)
        qc.mcx([problem_qubits[idx] for idx, _ in clause], result_ancilla)
        
        for idx, is_negated in clause:
            if is_negated:
                qc.x(problem_qubits[idx])

    # Define the 10 clauses: each (idx, negated) means variable x_idx or NOT x_idx
    clauses = [
        [(0, True), (2, True), (6, True)],    # (NOT x0 OR NOT x2 OR NOT x6)
        [(1, True), (4, False), (7, True)],   # (NOT x1 OR x4 OR NOT x7)
        [(0, True), (2, True), (4, False)],   # (NOT x0 OR NOT x2 OR x4)
        [(2, True), (6, False), (7, False)],  # (NOT x2 OR x6 OR x7)
        [(4, True), (5, True), (6, False)],   # (NOT x4 OR NOT x5 OR x6)
        [(1, True), (5, False), (7, True)],   # (NOT x1 OR x5 OR NOT x7)
        [(0, False), (2, False), (7, True)],  # (x0 OR x2 OR NOT x7)
        [(0, False), (4, True), (7, False)],  # (x0 OR NOT x4 OR x7)
        [(0, False), (1, False), (7, True)],  # (x0 OR x1 OR NOT x7)
        [(3, True), (6, True), (7, True)],    # (NOT x3 OR NOT x6 OR NOT x7)
    ]
    
    clause_ancillas = ancilla_qubits[0:10]
    result_ancilla = ancilla_qubits[10]
    
    # COMPUTE: evaluate each clause into its ancilla
    for i, clause in enumerate(clauses):
        compute_clause_satisfaction(qc, problem_qubits, clause, clause_ancillas[i])
    
    # Compute AND of all clause results into final ancilla
    qc.mcx(clause_ancillas, result_ancilla)
    
    # PHASE: apply -1 phase if all clauses satisfied
    qc.z(result_ancilla)
    
    # UNCOMPUTE: reverse the AND
    qc.mcx(clause_ancillas, result_ancilla)
    
    # UNCOMPUTE: reverse each clause evaluation (in reverse order)
    for i in range(9, -1, -1):
        uncompute_clause_satisfaction(qc, problem_qubits, clauses[i], clause_ancillas[i])
