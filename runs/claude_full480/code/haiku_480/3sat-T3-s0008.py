from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    def compute_clause(clause, ancilla):
        qubits = [problem_qubits[idx] for idx, _ in clause]
        is_negs = [is_neg for _, is_neg in clause]
        
        # Apply X to qubits that are not negated
        for q, is_neg in zip(qubits, is_negs):
            if not is_neg:
                qc.x(q)
        
        # Compute AND using mcx
        qc.mcx(qubits, ancilla)
        
        # Negate to get OR
        qc.x(ancilla)
        
        # Undo X flips
        for q, is_neg in zip(qubits, is_negs):
            if not is_neg:
                qc.x(q)
    
    clauses = [
        [(0, True), (2, True), (5, True)],
        [(1, True), (4, False), (5, True)],
        [(1, True), (2, False), (6, True)],
        [(1, True), (3, True), (4, False)],
        [(3, False), (4, False), (5, True)],
        [(2, False), (5, True), (6, False)],
        [(2, False), (3, True), (5, False)],
        [(0, True), (4, False), (5, True)],
        [(1, True), (2, True), (4, False)],
        [(1, False), (4, True), (5, False)],
    ]
    
    clause_ancillas = ancilla_qubits[:10]
    result_ancilla = ancilla_qubits[10]
    
    # Compute each clause
    for i, clause in enumerate(clauses):
        compute_clause(clause, clause_ancillas[i])
    
    # AND all clauses together
    qc.mcx(clause_ancillas, result_ancilla)
    
    # Apply phase
    qc.z(result_ancilla)
    
    # Uncompute AND
    qc.mcx(clause_ancillas, result_ancilla)
    
    # Uncompute clauses
    for i in range(len(clauses) - 1, -1, -1):
        compute_clause(clauses[i], clause_ancillas[i])
