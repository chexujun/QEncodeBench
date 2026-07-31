from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x = problem_qubits
    a = ancilla_qubits
    
    def compute_or_3_with_inverts(target, inverts):
        """Compute OR of 3 literals into target, with bit-wise inversions.
        inverts[i] = True means negate the i-th input before AND.
        Uses a[5] as temporary scratch.
        """
        q0, q1, q2 = x
        
        # Apply X gates to qubits that need inversion
        if inverts[0]:
            qc.x(q0)
        if inverts[1]:
            qc.x(q1)
        if inverts[2]:
            qc.x(q2)
        
        # Compute AND of the (possibly inverted) inputs
        # temp = q0 AND q1
        qc.ccx(q0, q1, a[5])
        # target = temp AND q2
        qc.ccx(a[5], q2, target)
        # Uncompute temp
        qc.ccx(q0, q1, a[5])
        
        # Apply X to target to convert AND to OR
        # (a OR b OR c) = NOT(NOT a AND NOT b AND NOT c)
        qc.x(target)
        
        # Unflip the problem qubits
        if inverts[2]:
            qc.x(q2)
        if inverts[1]:
            qc.x(q1)
        if inverts[0]:
            qc.x(q0)
    
    # Compute each clause into a[0]–a[4]
    # Clause 1: (NOT x0 OR x1 OR x2)
    compute_or_3_with_inverts(a[0], [False, True, True])
    
    # Clause 2: (x0 OR NOT x1 OR NOT x2)
    compute_or_3_with_inverts(a[1], [True, False, False])
    
    # Clause 3: (NOT x0 OR NOT x1 OR NOT x2)
    compute_or_3_with_inverts(a[2], [False, False, False])
    
    # Clause 4: (x0 OR x1 OR NOT x2)
    compute_or_3_with_inverts(a[3], [True, True, False])
    
    # Clause 5: (NOT x0 OR NOT x1 OR x2)
    compute_or_3_with_inverts(a[4], [False, False, True])
    
    # AND all clause results into a[5]
    qc.mcx([a[0], a[1], a[2], a[3], a[4]], a[5])
    
    # Apply phase gate
    qc.z(a[5])
    
    # Uncompute: reverse all operations
    qc.mcx([a[0], a[1], a[2], a[3], a[4]], a[5])
    compute_or_3_with_inverts(a[4], [False, False, True])
    compute_or_3_with_inverts(a[3], [True, True, False])
    compute_or_3_with_inverts(a[2], [False, False, False])
    compute_or_3_with_inverts(a[1], [True, False, False])
    compute_or_3_with_inverts(a[0], [False, True, True])
