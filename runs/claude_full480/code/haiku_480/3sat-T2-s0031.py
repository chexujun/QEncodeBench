from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    """
    Build a Grover-style phase oracle for the 3-SAT problem.
    Applies phase -1 to basis states that satisfy all 6 clauses.
    """
    x = problem_qubits
    a = ancilla_qubits
    
    # Define the 6 clauses as lists of (qubit_index, is_negated)
    clauses = [
        [(3, False), (4, True), (5, False)],   # (x3 OR NOT x4 OR x5)
        [(1, False), (2, True), (3, False)],   # (x1 OR NOT x2 OR x3)
        [(0, True), (1, True), (2, True)],     # (NOT x0 OR NOT x1 OR NOT x2)
        [(0, False), (1, True), (4, False)],   # (x0 OR NOT x1 OR x4)
        [(1, True), (2, False), (4, False)],   # (NOT x1 OR x2 OR x4)
        [(0, True), (1, False), (2, True)],    # (NOT x0 OR x1 OR NOT x2)
    ]
    
    # COMPUTE: evaluate each clause into its ancilla qubit
    for i, clause in enumerate(clauses):
        compute_clause(qc, x, clause, a[i])
    
    # AND all clause results into the final ancilla qubit
    qc.mcx(a[:6], a[6])
    
    # PHASE: apply Z to mark the solution
    qc.z(a[6])
    
    # UNCOMPUTE: reverse the AND
    qc.mcx(a[:6], a[6])
    
    # UNCOMPUTE: reverse each clause evaluation (in reverse order)
    for i in range(len(clauses) - 1, -1, -1):
        uncompute_clause(qc, x, clauses[i], a[i])


def compute_clause(qc, x, clause, anc):
    """
    Compute whether a clause is satisfied into the ancilla.
    Implements: OR(a,b,c) = NOT(AND(NOT a, NOT b, NOT c))
    """
    temp = [x[idx] for idx, _ in clause]
    
    # Flip problem qubits for negated terms
    for idx, is_neg in clause:
        if is_neg:
            qc.x(x[idx])
    
    # Compute AND of complements into ancilla
    for q in temp:
        qc.x(q)
    qc.mcx(temp, anc)
    for q in temp:
        qc.x(q)
    
    # Flip ancilla to convert AND-of-complements to OR
    qc.x(anc)
    
    # Flip back the problem qubits modified for negation
    for idx, is_neg in clause:
        if is_neg:
            qc.x(x[idx])


def uncompute_clause(qc, x, clause, anc):
    """Reverse of compute_clause - undoes all operations in reverse order."""
    temp = [x[idx] for idx, _ in clause]
    
    # Reverse order of compute_clause
    for idx, is_neg in clause:
        if is_neg:
            qc.x(x[idx])
    
    qc.x(anc)
    
    for q in temp:
        qc.x(q)
    qc.mcx(temp, anc)
    for q in temp:
        qc.x(q)
    
    for idx, is_neg in clause:
        if is_neg:
            qc.x(x[idx])
