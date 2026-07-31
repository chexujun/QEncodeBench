from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    pq = problem_qubits
    aq = ancilla_qubits
    
    # Define clauses as (qubit_index, negated) tuples
    # (x0 OR x4 OR NOT x5), (NOT x2 OR x4 OR NOT x5), ...
    clauses = [
        [(0, False), (4, False), (5, True)],
        [(2, True), (4, False), (5, True)],
        [(0, False), (1, False), (4, True)],
        [(1, True), (4, False), (5, False)],
        [(0, False), (2, True), (3, True)],
        [(1, False), (2, False), (3, False)],
    ]
    
    clause_ancs = aq[0:6]
    temp_anc = aq[6]
    
    # Compute each clause: OR(a,b,c) = NOT(AND(NOT a, NOT b, NOT c))
    for i, clause in enumerate(clauses):
        # Prepare inputs: flip non-negated terms to represent their negation
        for idx, negated in clause:
            if not negated:
                qc.x(pq[idx])
        
        # Start accumulator at 1
        qc.x(clause_ancs[i])
        
        # Compute AND and negate to get OR
        indices = [idx for idx, _ in clause]
        qc.ccx(pq[indices[0]], pq[indices[1]], temp_anc)
        qc.ccx(temp_anc, pq[indices[2]], clause_ancs[i])
        qc.ccx(pq[indices[0]], pq[indices[1]], temp_anc)
        
        # Restore problem qubits
        for idx, negated in clause:
            if not negated:
                qc.x(pq[idx])
    
    # Compute AND of all clauses into temp_anc
    qc.x(temp_anc)  # temp_anc = 1
    for i in range(6):
        qc.x(clause_ancs[i])  # Flip to get NOT clause
        qc.ccx(clause_ancs[i], temp_anc, temp_anc)
        qc.x(clause_ancs[i])  # Flip back
    
    # Apply phase
    qc.z(temp_anc)
    
    # Uncompute AND of clauses (same operations, self-inverse)
    for i in range(5, -1, -1):
        qc.x(clause_ancs[i])
        qc.ccx(clause_ancs[i], temp_anc, temp_anc)
        qc.x(clause_ancs[i])
    qc.x(temp_anc)  # temp_anc = 0
    
    # Uncompute each clause (reverse order)
    for i in range(5, -1, -1):
        clause = clauses[i]
        
        # Prepare inputs
        for idx, negated in clause:
            if not negated:
                qc.x(pq[idx])
        
        # Uncompute AND (self-inverse)
        indices = [idx for idx, _ in clause]
        qc.ccx(pq[indices[0]], pq[indices[1]], temp_anc)
        qc.ccx(temp_anc, pq[indices[2]], clause_ancs[i])
        qc.ccx(pq[indices[0]], pq[indices[1]], temp_anc)
        
        # Restore problem qubits
        for idx, negated in clause:
            if not negated:
                qc.x(pq[idx])
        
        # Restore clause ancilla
        qc.x(clause_ancs[i])
