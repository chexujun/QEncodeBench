from qiskit import QuantumCircuit
from qiskit.circuit.library import MCXGate

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x = problem_qubits
    a = ancilla_qubits
    
    # Define clauses: each is a list of (qubit_index, is_negated)
    clauses = [
        [(0, False), (1, False), (3, False)],          # (x0 OR x1 OR x3)
        [(2, True), (3, True), (4, False)],            # (NOT x2 OR NOT x3 OR x4)
        [(1, True), (2, False), (4, False)],           # (NOT x1 OR x2 OR x4)
        [(1, False), (2, False), (5, True)],           # (x1 OR x2 OR NOT x5)
        [(2, False), (3, False), (4, False)],          # (x2 OR x3 OR x4)
        [(0, True), (1, False), (3, True)],            # (NOT x0 OR x1 OR NOT x3)
        [(1, True), (2, True), (5, True)],             # (NOT x1 OR NOT x2 OR NOT x5)
        [(0, False), (4, True), (5, False)],           # (x0 OR NOT x4 OR x5)
        [(0, True), (2, False), (4, True)],            # (NOT x0 OR x2 OR NOT x4)
    ]
    
    result_ancilla = a[9]
    
    # COMPUTE: Evaluate each clause into its ancilla
    for clause_idx, clause_terms in enumerate(clauses):
        clause_ancilla = a[clause_idx]
        q0_idx, q0_neg = clause_terms[0]
        q1_idx, q1_neg = clause_terms[1]
        q2_idx, q2_neg = clause_terms[2]
        
        # To compute OR(L1, L2, L3) = NOT(NOT L1 AND NOT L2 AND NOT L3),
        # flip qubits for positive literals (to get NOT Li)
        if not q0_neg:
            qc.x(x[q0_idx])
        if not q1_neg:
            qc.x(x[q1_idx])
        if not q2_neg:
            qc.x(x[q2_idx])
        
        # Compute AND of the (transformed) literals
        qc.ccx(x[q0_idx], x[q1_idx], clause_ancilla)
        qc.cx(x[q2_idx], clause_ancilla)
        
        # Negate to get OR
        qc.x(clause_ancilla)
        
        # Restore problem qubits
        if not q2_neg:
            qc.x(x[q2_idx])
        if not q1_neg:
            qc.x(x[q1_idx])
        if not q0_neg:
            qc.x(x[q0_idx])
    
    # COMPUTE: AND all clause results into result_ancilla
    mcx_gate = MCXGate(9)
    qc.append(mcx_gate, [*a[0:9], result_ancilla])
    
    # PHASE: Apply Z to mark satisfying assignments
    qc.z(result_ancilla)
    
    # UNCOMPUTE: AND (reverse, using same MCX)
    qc.append(mcx_gate, [*a[0:9], result_ancilla])
    
    # UNCOMPUTE: Each clause in reverse order
    for clause_idx in range(len(clauses) - 1, -1, -1):
        clause_terms = clauses[clause_idx]
        clause_ancilla = a[clause_idx]
        q0_idx, q0_neg = clause_terms[0]
        q1_idx, q1_neg = clause_terms[1]
        q2_idx, q2_neg = clause_terms[2]
        
        # Flip qubits for positive literals
        if not q0_neg:
            qc.x(x[q0_idx])
        if not q1_neg:
            qc.x(x[q1_idx])
        if not q2_neg:
            qc.x(x[q2_idx])
        
        # Reverse the OR computation
        qc.x(clause_ancilla)
        qc.cx(x[q2_idx], clause_ancilla)
        qc.ccx(x[q0_idx], x[q1_idx], clause_ancilla)
        
        # Restore problem qubits
        if not q2_neg:
            qc.x(x[q2_idx])
        if not q1_neg:
            qc.x(x[q1_idx])
        if not q0_neg:
            qc.x(x[q0_idx])
