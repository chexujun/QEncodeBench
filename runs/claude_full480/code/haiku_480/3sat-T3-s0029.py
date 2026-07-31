from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    # Clause specifications: each is a list of (qubit_index, is_positive)
    clauses = [
        [(1, True), (4, False), (5, True)],   # (x1 OR NOT x4 OR x5)
        [(0, True), (1, True), (2, True)],    # (x0 OR x1 OR x2)
        [(1, True), (2, False), (5, False)],  # (x1 OR NOT x2 OR NOT x5)
        [(3, True), (4, False), (5, True)],   # (x3 OR NOT x4 OR x5)
        [(0, True), (4, True), (5, False)],   # (x0 OR x4 OR NOT x5)
        [(1, False), (4, False), (5, True)],  # (NOT x1 OR NOT x4 OR x5)
        [(0, False), (1, True), (2, True)],   # (NOT x0 OR x1 OR x2)
    ]
    
    def compute_clause(clause_idx):
        clause = clauses[clause_idx]
        ancilla = ancilla_qubits[clause_idx]
        
        # Compute NOT(AND of negated literals) = OR of literals
        # Using: (a OR b OR c) = NOT(NOT a AND NOT b AND NOT c)
        control_qubits = []
        flips = []
        for qubit_idx, is_positive in clause:
            qubit = problem_qubits[qubit_idx]
            if is_positive:
                qc.x(qubit)  # flip to negate positive literal
                flips.append(qubit)
            control_qubits.append(qubit)
        
        # Compute AND of all (negated) controls into ancilla
        qc.mcx(control_qubits, ancilla)
        
        # Flip back to restore problem qubits
        for qubit in flips:
            qc.x(qubit)
        
        # Negate ancilla to convert AND to OR
        qc.x(ancilla)
    
    # Compute all 7 clause ancillas
    for i in range(7):
        compute_clause(i)
    
    # Apply phase -1 when all clauses are satisfied (all ancillas are 1)
    work = ancilla_qubits[7]
    qc.mcx(ancilla_qubits[0:7], work)  # AND all clause ancillas into work
    qc.z(work)                          # Apply phase
    qc.mcx(ancilla_qubits[0:7], work)  # Uncompute AND
    
    # Uncompute all clause ancillas to restore them to |0>
    for i in range(6, -1, -1):
        compute_clause(i)
