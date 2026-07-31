from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    
    clauses = [
        [(0, False), (2, False), (4, False)],
        [(4, True), (6, False), (7, False)],
        [(0, False), (2, False), (7, False)],
        [(0, True), (2, True), (7, True)],
        [(0, False), (1, True), (2, True)],
        [(0, True), (3, False), (7, False)],
        [(2, False), (4, True), (7, False)],
        [(0, False), (6, True), (7, False)],
        [(3, False), (4, True), (6, False)],
        [(2, False), (6, False), (7, False)],
        [(1, False), (5, False), (7, True)],
    ]
    
    c = ancilla_qubits
    
    def or_into(qc, lit_qubit, lit_negated, result_qubit):
        """Compute result = result OR lit into result_qubit."""
        temp = c[11]
        
        qc.x(temp)
        qc.cx(result_qubit, temp)
        
        if lit_negated:
            qc.x(lit_qubit)
        qc.ccx(temp, lit_qubit, result_qubit)
        if lit_negated:
            qc.x(lit_qubit)
        
        qc.cx(result_qubit, temp)
        qc.x(temp)
    
    # Compute each clause
    for c_idx, clause in enumerate(clauses):
        q0, n0 = clause[0]
        q1, n1 = clause[1]
        q2, n2 = clause[2]
        
        if n0:
            qc.x(c[c_idx])
        qc.cx(problem_qubits[q0], c[c_idx])
        
        or_into(qc, problem_qubits[q1], n1, c[c_idx])
        or_into(qc, problem_qubits[q2], n2, c[c_idx])
    
    # AND all clause results together
    qc.x(c[11])
    
    for i in range(11):
        qc.x(c[i])
        qc.ccx(c[11], c[i], c[11])
        qc.x(c[i])
    
    # Apply Z phase gate
    qc.z(c[11])
    
    # UNCOMPUTE: reverse AND operations
    for i in range(10, -1, -1):
        qc.x(c[i])
        qc.ccx(c[11], c[i], c[11])
        qc.x(c[i])
    
    qc.x(c[11])
    
    # Uncompute each clause in reverse order
    for c_idx in range(10, -1, -1):
        q0, n0 = clauses[c_idx][0]
        q1, n1 = clauses[c_idx][1]
        q2, n2 = clauses[c_idx][2]
        
        temp = c[11]
        
        qc.x(temp)
        qc.cx(c[c_idx], temp)
        if n2:
            qc.x(problem_qubits[q2])
        qc.ccx(temp, problem_qubits[q2], c[c_idx])
        if n2:
            qc.x(problem_qubits[q2])
        qc.cx(c[c_idx], temp)
        qc.x(temp)
        
        qc.x(temp)
        qc.cx(c[c_idx], temp)
        if n1:
            qc.x(problem_qubits[q1])
        qc.ccx(temp, problem_qubits[q1], c[c_idx])
        if n1:
            qc.x(problem_qubits[q1])
        qc.cx(c[c_idx], temp)
        qc.x(temp)
        
        qc.cx(problem_qubits[q0], c[c_idx])
        if n0:
            qc.x(c[c_idx])
