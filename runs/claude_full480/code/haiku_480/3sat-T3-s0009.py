from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Define the 10 3-SAT clauses as (qubit_index, is_negated) tuples
    clauses = [
        [(0, True), (2, True), (4, True)],       # (¬x0 ∨ ¬x2 ∨ ¬x4)
        [(4, False), (6, False), (7, False)],    # (x4 ∨ x6 ∨ x7)
        [(0, False), (2, False), (6, False)],    # (x0 ∨ x2 ∨ x6)
        [(0, True), (6, True), (7, True)],       # (¬x0 ∨ ¬x6 ∨ ¬x7)
        [(1, True), (5, False), (7, False)],     # (¬x1 ∨ x5 ∨ x7)
        [(0, True), (4, False), (7, False)],     # (¬x0 ∨ x4 ∨ x7)
        [(1, True), (3, True), (7, True)],       # (¬x1 ∨ ¬x3 ∨ ¬x7)
        [(1, False), (3, False), (4, False)],    # (x1 ∨ x3 ∨ x4)
        [(2, True), (6, False), (7, True)],      # (¬x2 ∨ x6 ∨ ¬x7)
        [(2, True), (3, True), (4, True)],       # (¬x2 ∨ ¬x3 ∨ ¬x4)
    ]
    
    clause_ancillas = ancilla_qubits[:10]
    result_ancilla = ancilla_qubits[10]
    
    def compute_or_clause(clause, ancilla):
        # Compute: ancilla = OR(clause_literals)
        # Method: ancilla = NOT(AND(NOT(literal) for each literal))
        
        controls = [problem_qubits[idx] for idx, _ in clause]
        invert_mask = [is_negated for _, is_negated in clause]
        
        # Apply X to non-negated literals to invert them
        for i, do_invert in enumerate(invert_mask):
            if not do_invert:
                qc.x(controls[i])
        
        # Compute AND of inverted controls into ancilla
        qc.mcx(controls=controls, target=ancilla)
        
        # Restore non-negated literals
        for i, do_invert in enumerate(invert_mask):
            if not do_invert:
                qc.x(controls[i])
        
        # Flip ancilla to convert AND(NOT(...)) to OR(...)
        qc.x(ancilla)
    
    def uncompute_or_clause(clause, ancilla):
        # Reverse of compute_or_clause (computed -> phase -> uncompute discipline)
        
        controls = [problem_qubits[idx] for idx, _ in clause]
        invert_mask = [is_negated for _, is_negated in clause]
        
        # Undo X to ancilla
        qc.x(ancilla)
        
        # Undo restoration of non-negated literals
        for i, do_invert in enumerate(invert_mask):
            if not do_invert:
                qc.x(controls[i])
        
        # Undo AND computation
        qc.mcx(controls=controls, target=ancilla)
        
        # Undo inversion of non-negated literals
        for i, do_invert in enumerate(invert_mask):
            if not do_invert:
                qc.x(controls[i])
    
    # Compute each clause into its ancilla
    for i, clause in enumerate(clauses):
        compute_or_clause(clause, clause_ancillas[i])
    
    # AND all clauses into result_ancilla: result = c0 AND c1 AND ... AND c9
    qc.mcx(controls=clause_ancillas, target=result_ancilla)
    
    # Apply phase flip: -1 phase iff all clauses are satisfied
    qc.z(result_ancilla)
    
    # Uncompute the AND (mcx is self-inverse)
    qc.mcx(controls=clause_ancillas, target=result_ancilla)
    
    # Uncompute each clause in reverse order to restore ancillas to |0>
    for i in range(len(clauses) - 1, -1, -1):
        uncompute_or_clause(clauses[i], clause_ancillas[i])
