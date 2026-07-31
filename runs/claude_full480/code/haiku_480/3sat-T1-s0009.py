from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    q0, q1, q2 = problem_qubits[0], problem_qubits[1], problem_qubits[2]
    a0, a1, a2, a3, a4 = ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[2], ancilla_qubits[3], ancilla_qubits[4]
    
    def compute_or_clause(negate0, negate1, negate2, ancilla):
        """
        Compute an OR clause into ancilla using the identity:
        OR(a, b, c) = NOT(AND(NOT a, NOT b, NOT c))
        
        Negate flags indicate which qubits should be negated in the AND.
        """
        if negate0:
            qc.x(q0)
        if negate1:
            qc.x(q1)
        if negate2:
            qc.x(q2)
        
        qc.mcx([q0, q1, q2], ancilla)
        
        if negate0:
            qc.x(q0)
        if negate1:
            qc.x(q1)
        if negate2:
            qc.x(q2)
        
        qc.x(ancilla)
    
    # Compute each clause into ancilla qubits
    # Clause 1: (NOT x0 OR x1 OR NOT x2) → negate x1
    compute_or_clause(False, True, False, a0)
    # Clause 2: (NOT x0 OR x1 OR x2) → negate x1 and x2
    compute_or_clause(False, True, True, a1)
    # Clause 3: (x0 OR NOT x1 OR x2) → negate x0 and x2
    compute_or_clause(True, False, True, a2)
    # Clause 4: (NOT x0 OR NOT x1 OR x2) → negate x2
    compute_or_clause(False, False, True, a3)
    
    # AND all four clauses into a4
    qc.mcx([a0, a1, a2, a3], a4)
    
    # Apply phase -1 to solutions
    qc.z(a4)
    
    # Uncompute: reverse the AND
    qc.mcx([a0, a1, a2, a3], a4)
    
    # Uncompute clauses in reverse order
    compute_or_clause(False, False, True, a3)
    compute_or_clause(True, False, True, a2)
    compute_or_clause(False, True, True, a1)
    compute_or_clause(False, True, False, a0)
