from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x0, x1, x2 = problem_qubits[0], problem_qubits[1], problem_qubits[2]
    c = ancilla_qubits[:5]
    temp = ancilla_qubits[5]
    
    # Clauses with their negation indices:
    # (a OR b OR c) = NOT(NOT a AND NOT b AND NOT c)
    # Stored as (clause_ancilla, indices_to_negate_for_AND_condition)
    clauses = [
        (c[0], [1, 2]),  # (NOT x0 OR x1 OR x2)
        (c[1], [0, 1]),  # (x0 OR x1 OR NOT x2)
        (c[2], [0, 2]),  # (x0 OR NOT x1 OR x2)
        (c[3], [1, 2]),  # (NOT x0 OR x1 OR NOT x2)
        (c[4], [2]),     # (NOT x0 OR NOT x1 OR x2)
    ]
    
    # Compute each clause into its ancilla using compute-phase-uncompute
    for clause_ancilla, negations in clauses:
        qc.x(clause_ancilla)
        for neg in negations:
            qc.x(problem_qubits[neg])
        qc.mcx([x0, x1, x2], temp)
        for neg in negations:
            qc.x(problem_qubits[neg])
        qc.cx(temp, clause_ancilla)
        for neg in negations:
            qc.x(problem_qubits[neg])
        qc.mcx([x0, x1, x2], temp)
        for neg in negations:
            qc.x(problem_qubits[neg])
    
    # Compute AND of all clauses into temp
    qc.x(temp)
    for clause_ancilla in c:
        qc.x(clause_ancilla)
        qc.cx(clause_ancilla, temp)
        qc.x(clause_ancilla)
    
    # Apply phase
    qc.z(temp)
    
    # Uncompute AND of all clauses
    for clause_ancilla in reversed(c):
        qc.x(clause_ancilla)
        qc.cx(clause_ancilla, temp)
        qc.x(clause_ancilla)
    qc.x(temp)
    
    # Uncompute each clause in reverse order
    for clause_ancilla, negations in reversed(clauses):
        for neg in negations:
            qc.x(problem_qubits[neg])
        qc.mcx([x0, x1, x2], temp)
        for neg in negations:
            qc.x(problem_qubits[neg])
        qc.cx(temp, clause_ancilla)
        for neg in negations:
            qc.x(problem_qubits[neg])
        qc.mcx([x0, x1, x2], temp)
        for neg in negations:
            qc.x(problem_qubits[neg])
        qc.x(clause_ancilla)
