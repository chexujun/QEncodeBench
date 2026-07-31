from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list, ancilla_qubits: list) -> None:
    # Each clause: [(qubit_idx, polarity), ...]
    # polarity=True means literal appears positive; False means negated
    clauses = [
        [(1, True), (2, False), (5, True)],      # (x1 OR NOT x2 OR x5)
        [(2, False), (3, False), (4, False)],    # (NOT x2 OR NOT x3 OR NOT x4)
        [(3, True), (5, False), (6, False)],     # (x3 OR NOT x5 OR NOT x6)
        [(0, True), (4, False), (6, True)],      # (x0 OR NOT x4 OR x6)
        [(2, False), (5, False), (7, True)],     # (NOT x2 OR NOT x5 OR x7)
        [(0, False), (3, False), (7, False)],    # (NOT x0 OR NOT x3 OR NOT x7)
        [(4, False), (5, False), (6, True)],     # (NOT x4 OR NOT x5 OR x6)
        [(1, False), (4, True), (7, True)],      # (NOT x1 OR x4 OR x7)
    ]
    
    work = ancilla_qubits[8]
    clause_anc = ancilla_qubits[0:8]
    
    # COMPUTE: evaluate each clause into clause_anc[i]
    # For (a OR b OR c), compute clause_not_satisfied = (NOT a) AND (NOT b) AND (NOT c)
    for i, clause in enumerate(clauses):
        qubits = [problem_qubits[clause[j][0]] for j in range(3)]
        polarities = [clause[j][1] for j in range(3)]
        
        # Apply X to flip qubits for positive literals (since we want their negations for the AND)
        for j in range(3):
            if polarities[j]:
                qc.x(qubits[j])
        
        # Compute AND(q0, q1, q2) into clause_anc[i]
        qc.ccx(qubits[0], qubits[1], work)
        qc.ccx(work, qubits[2], clause_anc[i])
        qc.ccx(qubits[0], qubits[1], work)
        
        # Restore X gates
        for j in range(3):
            if polarities[j]:
                qc.x(qubits[j])
    
    # Invert to get clause_satisfied[i] = NOT clause_not_satisfied[i]
    for i in range(8):
        qc.x(clause_anc[i])
    
    # Compute AND of all clauses into work_anc
    # Build AND chain: result = c0 AND c1 AND c2 AND ... AND c7
    qc.ccx(clause_anc[0], clause_anc[1], work)
    qc.ccx(work, clause_anc[2], clause_anc[0])
    qc.ccx(clause_anc[0], clause_anc[3], clause_anc[1])
    qc.ccx(clause_anc[1], clause_anc[4], clause_anc[2])
    qc.ccx(clause_anc[2], clause_anc[5], clause_anc[3])
    qc.ccx(clause_anc[3], clause_anc[6], clause_anc[4])
    qc.ccx(clause_anc[4], clause_anc[7], work)
    
    # PHASE: apply Z when formula is satisfied
    qc.z(work)
    
    # UNCOMPUTE: reverse the AND chain
    qc.ccx(clause_anc[4], clause_anc[7], work)
    qc.ccx(clause_anc[3], clause_anc[6], clause_anc[4])
    qc.ccx(clause_anc[2], clause_anc[5], clause_anc[3])
    qc.ccx(clause_anc[1], clause_anc[4], clause_anc[2])
    qc.ccx(clause_anc[0], clause_anc[3], clause_anc[1])
    qc.ccx(work, clause_anc[2], clause_anc[0])
    qc.ccx(clause_anc[0], clause_anc[1], work)
    
    # Unflip clause ancillas
    for i in range(8):
        qc.x(clause_anc[i])
    
    # Uncompute clause evaluations in reverse order
    for i in range(7, -1, -1):
        qubits = [problem_qubits[clauses[i][j][0]] for j in range(3)]
        polarities = [clauses[i][j][1] for j in range(3)]
        
        for j in range(3):
            if polarities[j]:
                qc.x(qubits[j])
        
        qc.ccx(qubits[0], qubits[1], work)
        qc.ccx(work, qubits[2], clause_anc[i])
        qc.ccx(qubits[0], qubits[1], work)
        
        for j in range(3):
            if polarities[j]:
                qc.x(qubits[j])
