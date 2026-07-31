from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Define clauses as (variable_index, negation_flag) tuples
    clauses = [
        [(2, True), (4, True), (6, True)],        # (NOT x2 OR NOT x4 OR NOT x6)
        [(4, False), (5, False), (6, True)],      # (x4 OR x5 OR NOT x6)
        [(0, True), (1, False), (3, True)],       # (NOT x0 OR x1 OR NOT x3)
        [(0, True), (3, False), (4, True)],       # (NOT x0 OR x3 OR NOT x4)
        [(3, True), (5, False), (6, False)],      # (NOT x3 OR x5 OR x6)
        [(1, True), (2, True), (6, False)],       # (NOT x1 OR NOT x2 OR x6)
        [(0, True), (3, False), (5, False)],      # (NOT x0 OR x3 OR x5)
        [(0, False), (5, True), (6, True)],       # (x0 OR NOT x5 OR NOT x6)
        [(0, False), (3, True), (5, True)],       # (x0 OR NOT x3 OR NOT x5)
        [(0, False), (1, False), (2, True)],      # (x0 OR x1 OR NOT x2)
    ]
    
    clause_ancillas = ancilla_qubits[:10]
    work_ancilla = ancilla_qubits[10]
    
    # COMPUTE PHASE: Compute each clause result
    for i, clause in enumerate(clauses):
        q0_idx, neg0 = clause[0]
        q1_idx, neg1 = clause[1]
        q2_idx, neg2 = clause[2]
        
        q0 = problem_qubits[q0_idx]
        q1 = problem_qubits[q1_idx]
        q2 = problem_qubits[q2_idx]
        result = clause_ancillas[i]
        work = work_ancilla
        
        # Apply X gates to flip qubits that need negation
        if neg0: qc.x(q0)
        if neg1: qc.x(q1)
        if neg2: qc.x(q2)
        
        # Compute (q0 OR q1) into work using: (a OR b) = a XOR b XOR (a AND b)
        qc.cx(q0, work)           # work = a
        qc.cx(q1, work)           # work = a XOR b
        qc.ccx(q0, q1, work)      # work = a XOR b XOR (a AND b)
        
        # Compute (work OR q2) into result using same formula
        qc.cx(work, result)       # result = work
        qc.cx(q2, result)         # result = work XOR q2
        qc.ccx(work, q2, result)  # result = (work OR q2)
        
        # Uncompute work_ancilla back to |0>
        qc.ccx(q0, q1, work)
        qc.cx(q1, work)
        qc.cx(q0, work)
        
        # Undo negations (restore problem qubits)
        if neg2: qc.x(q2)
        if neg1: qc.x(q1)
        if neg0: qc.x(q0)
    
    # Compute AND of all clause results using multi-controlled X
    qc.mcx(clause_ancillas, work_ancilla)
    
    # Apply Z phase (marks solutions with -1)
    qc.z(work_ancilla)
    
    # Uncompute AND to return work_ancilla to |0>
    qc.mcx(clause_ancillas, work_ancilla)
    
    # UNCOMPUTE PHASE: Reverse the clause computations
    for i in range(len(clauses) - 1, -1, -1):
        q0_idx, neg0 = clauses[i][0]
        q1_idx, neg1 = clauses[i][1]
        q2_idx, neg2 = clauses[i][2]
        
        q0 = problem_qubits[q0_idx]
        q1 = problem_qubits[q1_idx]
        q2 = problem_qubits[q2_idx]
        result = clause_ancillas[i]
        work = work_ancilla
        
        # Apply negations again (will be undone at the end)
        if neg0: qc.x(q0)
        if neg1: qc.x(q1)
        if neg2: qc.x(q2)
        
        # Reverse the OR computation
        qc.cx(q0, work)
        qc.cx(q1, work)
        qc.ccx(q0, q1, work)
        
        qc.ccx(work, q2, result)
        qc.cx(q2, result)
        qc.cx(work, result)
        
        qc.ccx(q0, q1, work)
        qc.cx(q1, work)
        qc.cx(q0, work)
        
        # Undo negations
        if neg2: qc.x(q2)
        if neg1: qc.x(q1)
        if neg0: qc.x(q0)
