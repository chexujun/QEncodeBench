from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    
    # Define the 3-SAT clauses as (qubit_index, is_positive) pairs
    # is_positive=True means the literal is x_i; False means NOT x_i
    clauses = [
        [(2, True), (5, True), (6, False)],   # (x2 OR x5 OR NOT x6)
        [(0, False), (2, True), (7, False)],  # (NOT x0 OR x2 OR NOT x7)
        [(0, False), (2, False), (4, True)],  # (NOT x0 OR NOT x2 OR x4)
        [(2, True), (5, False), (6, True)],   # (x2 OR NOT x5 OR x6)
        [(1, True), (5, True), (7, True)],    # (x1 OR x5 OR x7)
        [(2, True), (3, True), (5, False)],   # (x2 OR x3 OR NOT x5)
        [(2, False), (4, False), (6, False)], # (NOT x2 OR NOT x4 OR NOT x6)
        [(0, False), (3, True), (7, True)],   # (NOT x0 OR x3 OR x7)
        [(1, False), (2, True), (3, True)],   # (NOT x1 OR x2 OR x3)
        [(0, False), (3, True), (5, True)],   # (NOT x0 OR x3 OR x5)
    ]
    
    clause_ancillas = ancilla_qubits[:10]
    result_ancilla = ancilla_qubits[10]
    
    # Compute each clause: for (L1 OR L2 OR L3), compute NOT(L1 OR L2 OR L3) = 
    # (NOT L1) AND (NOT L2) AND (NOT L3) into ancilla, then negate
    for clause_idx, clause in enumerate(clauses):
        lit_qubits = []
        for qubit_index, is_positive in clause:
            if is_positive:
                lit_qubits.append(problem_qubits[qubit_index])
                qc.x(problem_qubits[qubit_index])  # Invert to get NOT x_i
            else:
                lit_qubits.append(problem_qubits[qubit_index])  # Already NOT
        
        # Multi-controlled-X: ancilla flipped iff (NOT L1) AND (NOT L2) AND (NOT L3)
        qc.mcx(control_qubits=lit_qubits, target_qubit=clause_ancillas[clause_idx])
        
        # Undo inversions
        for qubit_index, is_positive in clause:
            if is_positive:
                qc.x(problem_qubits[qubit_index])
        
        # Negate to convert from "clause unsatisfied" to "clause satisfied"
        qc.x(clause_ancillas[clause_idx])
    
    # AND all clause ancillas: result_ancilla = 1 iff all clauses satisfied
    qc.mcx(control_qubits=clause_ancillas, target_qubit=result_ancilla)
    
    # Apply phase -1
    qc.z(result_ancilla)
    
    # Uncompute the AND
    qc.mcx(control_qubits=clause_ancillas, target_qubit=result_ancilla)
    
    # Uncompute each clause (reverse order)
    for clause_idx in range(len(clauses)):
        clause = clauses[clause_idx]
        
        qc.x(clause_ancillas[clause_idx])  # Undo final negation
        
        lit_qubits = []
        for qubit_index, is_positive in clause:
            if is_positive:
                lit_qubits.append(problem_qubits[qubit_index])
                qc.x(problem_qubits[qubit_index])
            else:
                lit_qubits.append(problem_qubits[qubit_index])
        
        qc.mcx(control_qubits=lit_qubits, target_qubit=clause_ancillas[clause_idx])
        
        for qubit_index, is_positive in clause:
            if is_positive:
                qc.x(problem_qubits[qubit_index])
