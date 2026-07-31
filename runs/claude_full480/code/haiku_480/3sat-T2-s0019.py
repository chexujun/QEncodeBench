from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x = problem_qubits
    a = ancilla_qubits
    
    def compute_formula():
        """
        Compute the 3-SAT formula into a[0].
        Formula: (x0 OR NOT x1 OR x2) AND (x1 OR NOT x2 OR x3) AND
                 (x1 OR x2 OR x3) AND (x1 OR NOT x2 OR NOT x3) AND
                 (x0 OR NOT x1 OR x3)
        """
        
        # Initialize a[0] to 1
        qc.x(a[0])
        
        # Clause 1: (x0 OR NOT x1 OR x2)
        compute_or_clause([0, 1, 2], [False, True, False])
        and_into_a0()
        
        # Clause 2: (x1 OR NOT x2 OR x3)
        compute_or_clause([1, 2, 3], [False, True, False])
        and_into_a0()
        
        # Clause 3: (x1 OR x2 OR x3)
        compute_or_clause([1, 2, 3], [False, False, False])
        and_into_a0()
        
        # Clause 4: (x1 OR NOT x2 OR NOT x3)
        compute_or_clause([1, 2, 3], [False, True, True])
        and_into_a0()
        
        # Clause 5: (x0 OR NOT x1 OR x3)
        compute_or_clause([0, 1, 3], [False, True, False])
        and_into_a0()
    
    def compute_or_clause(var_indices, negations):
        """
        Compute (lit0 OR lit1 OR lit2) into a[1].
        Using: OR = NOT(AND of NOTs)
        """
        # Compute (NOT lit0)
        if negations[0]:
            qc.cx(x[var_indices[0]], a[2])
        else:
            qc.x(a[2])
            qc.cx(x[var_indices[0]], a[2])
        
        # Compute (NOT lit1)
        if negations[1]:
            qc.cx(x[var_indices[1]], a[3])
        else:
            qc.x(a[3])
            qc.cx(x[var_indices[1]], a[3])
        
        # Compute (NOT lit0) AND (NOT lit1)
        qc.ccx(a[2], a[3], a[4])
        
        # Compute (NOT lit2)
        if negations[2]:
            qc.cx(x[var_indices[2]], a[5])
        else:
            qc.x(a[5])
            qc.cx(x[var_indices[2]], a[5])
        
        # Compute ((NOT lit0) AND (NOT lit1)) AND (NOT lit2)
        qc.ccx(a[4], a[5], a[1])
        
        # Negate to get the OR clause
        qc.x(a[1])
        
        # Uncompute
        qc.ccx(a[4], a[5], a[1])
        if negations[2]:
            qc.cx(x[var_indices[2]], a[5])
        else:
            qc.cx(x[var_indices[2]], a[5])
            qc.x(a[5])
        qc.ccx(a[2], a[3], a[4])
        if negations[1]:
            qc.cx(x[var_indices[1]], a[3])
        else:
            qc.cx(x[var_indices[1]], a[3])
            qc.x(a[3])
        if negations[0]:
            qc.cx(x[var_indices[0]], a[2])
        else:
            qc.cx(x[var_indices[0]], a[2])
            qc.x(a[2])
    
    def and_into_a0():
        """Compute a[0] = a[0] AND a[1]"""
        qc.ccx(a[0], a[1], a[2])
        qc.cx(a[2], a[0])
        qc.cx(a[0], a[2])
        qc.cx(a[2], a[0])
    
    # Compute-phase-uncompute
    compute_formula()
    qc.z(a[0])
    compute_formula()
