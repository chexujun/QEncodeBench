from qiskit import QuantumCircuit
from math import pi

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Define the 10 clauses: each is (qubit_indices, negate_flags)
    clauses = [
        ([0, 6, 7], [False, False, False]),  # (x0 OR x6 OR x7)
        ([1, 3, 7], [True, True, False]),    # (NOT x1 OR NOT x3 OR x7)
        ([1, 3, 4], [False, True, False]),   # (x1 OR NOT x3 OR x4)
        ([0, 6, 7], [False, False, True]),   # (x0 OR x6 OR NOT x7)
        ([2, 5, 7], [True, True, False]),    # (NOT x2 OR NOT x5 OR x7)
        ([1, 5, 6], [False, True, True]),    # (x1 OR NOT x5 OR NOT x6)
        ([1, 3, 6], [True, False, False]),   # (NOT x1 OR x3 OR x6)
        ([1, 4, 5], [True, False, True]),    # (NOT x1 OR x4 OR NOT x5)
        ([4, 5, 7], [False, True, True]),    # (x4 OR NOT x5 OR NOT x7)
        ([2, 4, 7], [True, True, True]),     # (NOT x2 OR NOT x4 OR NOT x7)
    ]
    
    clause_ancillas = ancilla_qubits[0:10]
    temp_ancilla = ancilla_qubits[10]
    
    def compute_or3(q_indices, n_flags, output_ancilla):
        """Compute OR of 3 qubits (with optional negations) into output_ancilla.
        Uses formula: (a OR b OR c) = NOT((NOT a) AND (NOT b) AND (NOT c))
        """
        q0, q1, q2 = q_indices
        n0, n1, n2 = n_flags
        
        # Apply X gates to flip qubits where negation is NOT needed
        # (so the AND computes the negations correctly)
        if not n0:
            qc.x(problem_qubits[q0])
        if not n1:
            qc.x(problem_qubits[q1])
        if not n2:
            qc.x(problem_qubits[q2])
        
        # Compute AND of the three qubits into output_ancilla
        # temp_ancilla = q0 AND q1
        qc.ccx(problem_qubits[q0], problem_qubits[q1], temp_ancilla)
        # output_ancilla = temp_ancilla AND q2
        qc.ccx(temp_ancilla, problem_qubits[q2], output_ancilla)
        # Uncompute temp_ancilla
        qc.ccx(problem_qubits[q0], problem_qubits[q1], temp_ancilla)
        
        # Negate output to convert AND to OR
        qc.x(output_ancilla)
        
        # Restore problem qubits to original state
        if not n0:
            qc.x(problem_qubits[q0])
        if not n1:
            qc.x(problem_qubits[q1])
        if not n2:
            qc.x(problem_qubits[q2])
    
    # Compute all 10 clause results into ancillas 0-9
    for i, (q_indices, n_flags) in enumerate(clauses):
        compute_or3(q_indices, n_flags, clause_ancillas[i])
    
    # Apply phase oracle using the |-⟩ trick
    # Prepare temp_ancilla in eigenstate |-⟩ of X with eigenvalue -1
    qc.x(temp_ancilla)
    qc.h(temp_ancilla)
    
    # Multi-controlled X: flips |-⟩ to -|-⟩ when all clause ancillas are 1
    # This applies phase -1 to the entire state iff all clauses are satisfied
    qc.mcx(clause_ancillas, temp_ancilla)
    
    # Restore temp_ancilla to |0⟩ (reversing the |-⟩ preparation)
    qc.h(temp_ancilla)
    qc.x(temp_ancilla)
    
    # Uncompute clause results in reverse order
    # (operations are self-inverse, so same sequence reverses the computation)
    for i in range(len(clauses) - 1, -1, -1):
        q_indices, n_flags = clauses[i]
        compute_or3(q_indices, n_flags, clause_ancillas[i])
