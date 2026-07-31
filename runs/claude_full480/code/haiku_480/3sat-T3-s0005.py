from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    """
    Grover oracle for 3-SAT: applies phase -1 to basis states satisfying all clauses.
    """
    clauses = [
        [(0, False), (2, False), (4, True)],   # (x0 OR x2 OR NOT x4)
        [(0, True), (3, False), (5, True)],    # (NOT x0 OR x3 OR NOT x5)
        [(2, False), (3, True), (5, True)],    # (x2 OR NOT x3 OR NOT x5)
        [(2, True), (3, False), (6, True)],    # (NOT x2 OR x3 OR NOT x6)
        [(2, False), (4, False), (5, True)],   # (x2 OR x4 OR NOT x5)
        [(0, False), (3, True), (7, True)],    # (x0 OR NOT x3 OR NOT x7)
        [(1, False), (2, True), (4, False)],   # (x1 OR NOT x2 OR x4)
        [(2, True), (3, True), (5, False)],    # (NOT x2 OR NOT x3 OR x5)
        [(1, True), (2, False), (4, True)],    # (NOT x1 OR x2 OR NOT x4)
        [(0, True), (1, False), (2, True)],    # (NOT x0 OR x1 OR NOT x2)
    ]
    
    num_clauses = len(clauses)
    clause_ancillas = ancilla_qubits[:num_clauses]
    work_anc = ancilla_qubits[num_clauses]
    
    # COMPUTE: Evaluate each clause into clause_ancillas
    for c_idx, clause in enumerate(clauses):
        c_anc = clause_ancillas[c_idx]
        
        # Identify which literals in the clause are false (clause not satisfied)
        controls_to_negate = []
        controls_positive = []
        
        for q_idx, is_negated in clause:
            q = problem_qubits[q_idx]
            # Clause is NOT satisfied iff all literals are false
            # Literal is false when: (not is_negated and q=0) or (is_negated and q=1)
            if is_negated:
                # Literal (NOT q) is false when q=1 (positive control)
                controls_positive.append(q)
            else:
                # Literal q is false when q=0 (need to negate: control on NOT q)
                controls_to_negate.append(q)
        
        all_controls = controls_positive + controls_to_negate
        
        # Compute AND: work_anc = 1 iff clause is NOT satisfied
        for q in controls_to_negate:
            qc.x(q)
        qc.mcx(all_controls, work_anc)
        for q in controls_to_negate:
            qc.x(q)
        
        # Set clause_anc = NOT work_anc (1 iff clause IS satisfied)
        qc.x(c_anc)
        qc.cx(work_anc, c_anc)
        
        # Reset work_anc to 0 for next clause
        for q in controls_to_negate:
            qc.x(q)
        qc.mcx(all_controls, work_anc)
        for q in controls_to_negate:
            qc.x(q)
    
    # COMPUTE: AND all clause results into work_anc
    qc.mcx(clause_ancillas, work_anc)
    
    # Apply phase -1 if all clauses satisfied
    qc.z(work_anc)
    
    # UNCOMPUTE: AND
    qc.mcx(clause_ancillas, work_anc)
    
    # UNCOMPUTE: Each clause (in reverse order)
    for c_idx in range(num_clauses - 1, -1, -1):
        c_anc = clause_ancillas[c_idx]
        clause = clauses[c_idx]
        
        controls_to_negate = []
        controls_positive = []
        
        for q_idx, is_negated in clause:
            q = problem_qubits[q_idx]
            if is_negated:
                controls_positive.append(q)
            else:
                controls_to_negate.append(q)
        
        all_controls = controls_positive + controls_to_negate
        
        # Undo reset work_anc
        for q in controls_to_negate:
            qc.x(q)
        qc.mcx(all_controls, work_anc)
        for q in controls_to_negate:
            qc.x(q)
        
        # Undo set clause_anc
        qc.cx(work_anc, c_anc)
        qc.x(c_anc)
        
        # Undo compute AND
        for q in controls_to_negate:
            qc.x(q)
        qc.mcx(all_controls, work_anc)
        for q in controls_to_negate:
            qc.x(q)
