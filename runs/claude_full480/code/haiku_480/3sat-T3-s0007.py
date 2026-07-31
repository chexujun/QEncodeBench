from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # For each clause, store the literals whose AND equals the clause's negation
    # clause_negated[i] contains (qubit_idx, is_negated) pairs such that:
    #   ancilla[i] = 1 iff all these literals evaluate to True
    #   which means the clause i is False
    clauses_negated = [
        [(0, True), (1, False), (2, False)],    # (NOT x0) AND x1 AND x2
        [(1, True), (2, False), (4, False)],    # (NOT x1) AND x2 AND x4
        [(2, True), (4, False), (5, False)],    # (NOT x2) AND x4 AND x5
        [(1, False), (3, True), (5, False)],    # x1 AND (NOT x3) AND x5
        [(2, False), (3, True), (5, True)],     # x2 AND (NOT x3) AND (NOT x5)
        [(2, True), (4, True), (5, False)],     # (NOT x2) AND (NOT x4) AND x5
        [(3, False), (4, True), (5, False)],    # x3 AND (NOT x4) AND x5
        [(0, True), (2, True), (6, True)],      # (NOT x0) AND (NOT x2) AND (NOT x6)
        [(3, False), (4, False), (6, False)],   # x3 AND x4 AND x6
    ]
    
    clause_ancillas = ancilla_qubits[0:9]
    final_ancilla = ancilla_qubits[9]
    
    # COMPUTE: For each clause, compute its negation
    for i, clause_neg in enumerate(clauses_negated):
        ancilla = clause_ancillas[i]
        controls = []
        
        # Flip negated qubits and build control list
        for qubit_idx, is_negated in clause_neg:
            if is_negated:
                qc.x(problem_qubits[qubit_idx])
            controls.append(problem_qubits[qubit_idx])
        
        # Multi-controlled X: ancilla flips if all controls are 1
        qc.mcx(controls, ancilla)
        
        # Restore negated qubits
        for qubit_idx, is_negated in clause_neg:
            if is_negated:
                qc.x(problem_qubits[qubit_idx])
    
    # Convert: ancilla[i] = 1 iff clause i is TRUE (flip those that detect False)
    for ancilla in clause_ancillas:
        qc.x(ancilla)
    
    # Compute AND of all clause results
    qc.mcx(clause_ancillas, final_ancilla)
    
    # PHASE: Apply Z to mark satisfying assignments with phase -1
    qc.z(final_ancilla)
    
    # UNCOMPUTE: Reverse all operations in reverse order
    qc.mcx(clause_ancillas, final_ancilla)
    
    for ancilla in clause_ancillas:
        qc.x(ancilla)
    
    for i, clause_neg in enumerate(clauses_negated):
        ancilla = clause_ancillas[i]
        controls = []
        
        for qubit_idx, is_negated in clause_neg:
            if is_negated:
                qc.x(problem_qubits[qubit_idx])
            controls.append(problem_qubits[qubit_idx])
        
        qc.mcx(controls, ancilla)
        
        for qubit_idx, is_negated in clause_neg:
            if is_negated:
                qc.x(problem_qubits[qubit_idx])
