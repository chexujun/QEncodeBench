from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x = problem_qubits
    a = ancilla_qubits
    
    # Define the 9 clauses as lists of (qubit_index, is_negated)
    clauses = [
        [(1, True), (3, True), (6, False)],   # (NOT x1 OR NOT x3 OR x6)
        [(1, False), (6, False), (7, True)],  # (x1 OR x6 OR NOT x7)
        [(2, True), (5, False), (6, True)],   # (NOT x2 OR x5 OR NOT x6)
        [(2, True), (3, True), (7, True)],    # (NOT x2 OR NOT x3 OR NOT x7)
        [(0, False), (1, False), (6, True)],  # (x0 OR x1 OR NOT x6)
        [(0, True), (1, False), (3, False)],  # (NOT x0 OR x1 OR x3)
        [(2, False), (3, True), (6, True)],   # (x2 OR NOT x3 OR NOT x6)
        [(1, False), (4, True), (6, True)],   # (x1 OR NOT x4 OR NOT x6)
        [(2, True), (6, True), (7, False)],   # (NOT x2 OR NOT x6 OR x7)
    ]
    
    # COMPUTE: evaluate each clause into ancillas 0-8
    for c_idx, clause in enumerate(clauses):
        compute_or_clause(qc, x, clause, a[c_idx], a[9])
    
    # COMPUTE: AND all clauses using ancilla 9
    qc.x(a[9])  # Initialize to 1
    for c_idx in range(9):
        qc.ccx(a[c_idx], a[9], a[9])  # a[9] becomes 0 if any clause is false
    
    # PHASE: Apply Z gate controlled by the AND result
    qc.z(a[9])
    
    # UNCOMPUTE: reverse the AND operation
    for c_idx in range(9):
        qc.ccx(a[c_idx], a[9], a[9])
    qc.x(a[9])
    
    # UNCOMPUTE: reverse each clause evaluation
    for c_idx in range(8, -1, -1):
        uncompute_or_clause(qc, x, clauses[c_idx], a[c_idx], a[9])


def compute_or_clause(qc, x, clause, result_ancilla, aux_ancilla):
    """Compute OR of literals into result_ancilla using compute-phase-uncompute."""
    q0_idx, neg0 = clause[0]
    q1_idx, neg1 = clause[1]
    q2_idx, neg2 = clause[2]
    
    # Apply X gates for negated literals
    if neg0:
        qc.x(q0_idx)
    if neg1:
        qc.x(q1_idx)
    if neg2:
        qc.x(q2_idx)
    
    # Compute tmp = q0 OR q1 into aux_ancilla
    qc.cx(q0_idx, aux_ancilla)
    qc.cx(q1_idx, aux_ancilla)
    qc.ccx(q0_idx, q1_idx, aux_ancilla)
    
    # Compute result = tmp OR q2 into result_ancilla
    qc.cx(aux_ancilla, result_ancilla)
    qc.cx(q2_idx, result_ancilla)
    qc.ccx(aux_ancilla, q2_idx, result_ancilla)
    
    # Uncompute tmp back to 0
    qc.ccx(q0_idx, q1_idx, aux_ancilla)
    qc.cx(q1_idx, aux_ancilla)
    qc.cx(q0_idx, aux_ancilla)
    
    # Undo X gates for negated literals
    if neg2:
        qc.x(q2_idx)
    if neg1:
        qc.x(q1_idx)
    if neg0:
        qc.x(q0_idx)


def uncompute_or_clause(qc, x, clause, result_ancilla, aux_ancilla):
    """Uncompute OR of literals from result_ancilla (mirror of compute)."""
    q0_idx, neg0 = clause[0]
    q1_idx, neg1 = clause[1]
    q2_idx, neg2 = clause[2]
    
    # Apply X gates for negated literals
    if neg0:
        qc.x(q0_idx)
    if neg1:
        qc.x(q1_idx)
    if neg2:
        qc.x(q2_idx)
    
    # Recompute tmp = q0 OR q1 (needed for uncomputation)
    qc.cx(q0_idx, aux_ancilla)
    qc.cx(q1_idx, aux_ancilla)
    qc.ccx(q0_idx, q1_idx, aux_ancilla)
    
    # Uncompute result = tmp OR q2
    qc.ccx(aux_ancilla, q2_idx, result_ancilla)
    qc.cx(q2_idx, result_ancilla)
    qc.cx(aux_ancilla, result_ancilla)
    
    # Uncompute tmp back to 0
    qc.ccx(q0_idx, q1_idx, aux_ancilla)
    qc.cx(q1_idx, aux_ancilla)
    qc.cx(q0_idx, aux_ancilla)
    
    # Undo X gates for negated literals
    if neg2:
        qc.x(q2_idx)
    if neg1:
        qc.x(q1_idx)
    if neg0:
        qc.x(q0_idx)
