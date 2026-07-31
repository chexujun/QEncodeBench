from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    
    def compute_or_clause(literals, ancilla):
        # Compute (l1 OR l2 OR l3) into ancilla using:
        # NOT(a OR b OR c) = (NOT a AND NOT b AND NOT c), then flip result
        
        # Flip qubits that are not negated in the clause
        for qubit_idx, is_negated in literals:
            if not is_negated:
                qc.x(problem_qubits[qubit_idx])
        
        # Compute AND of adjusted controls into ancilla
        control_qubits = [problem_qubits[qubit_idx] for qubit_idx, _ in literals]
        
        if len(control_qubits) == 1:
            qc.cx(control_qubits[0], ancilla)
        elif len(control_qubits) == 2:
            qc.ccx(control_qubits[0], control_qubits[1], ancilla)
        elif len(control_qubits) == 3:
            qc.mcx(control_qubits, ancilla)
        
        # Restore flipped qubits
        for qubit_idx, is_negated in literals:
            if not is_negated:
                qc.x(problem_qubits[qubit_idx])
        
        # Flip ancilla to get OR
        qc.x(ancilla)
    
    # Define clauses as lists of (qubit_idx, is_negated)
    clauses = [
        [(0, False), (1, False), (7, False)],  # (x0 OR x1 OR x7)
        [(3, True), (4, False), (6, False)],   # (NOT x3 OR x4 OR x6)
        [(0, False), (2, True), (4, True)],    # (x0 OR NOT x2 OR NOT x4)
        [(0, False), (1, True), (3, True)],    # (x0 OR NOT x1 OR NOT x3)
        [(0, True), (6, False), (7, False)],   # (NOT x0 OR x6 OR x7)
        [(5, False), (6, True), (7, True)],    # (x5 OR NOT x6 OR NOT x7)
        [(0, False), (4, True), (6, False)],   # (x0 OR NOT x4 OR x6)
        [(0, False), (6, True), (7, True)],    # (x0 OR NOT x6 OR NOT x7)
    ]
    
    clause_ancillas = ancilla_qubits[0:8]
    final_result = ancilla_qubits[8]
    
    # Compute each clause into its ancilla
    for i in range(8):
        compute_or_clause(clauses[i], clause_ancillas[i])
    
    # AND all clauses together using Toffoli ladder
    qc.cx(clause_ancillas[0], final_result)
    for i in range(1, 8):
        qc.ccx(final_result, clause_ancillas[i], final_result)
    
    # Apply phase -1
    qc.z(final_result)
    
    # Uncompute AND (reverse order)
    for i in range(7, 0, -1):
        qc.ccx(final_result, clause_ancillas[i], final_result)
    qc.cx(clause_ancillas[0], final_result)
    
    # Uncompute clauses (reverse order)
    for i in range(7, -1, -1):
        compute_or_clause(clauses[i], clause_ancillas[i])
