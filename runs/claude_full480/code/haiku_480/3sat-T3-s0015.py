from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    
    # 3-SAT clauses: (variable_indices, negation_flags)
    clauses = [
        ([1, 2, 4], [False, False, False]),    # (x1 OR x2 OR x4)
        ([1, 2, 3], [False, False, False]),    # (x1 OR x2 OR x3)
        ([0, 5, 6], [True, True, True]),       # (NOT x0 OR NOT x5 OR NOT x6)
        ([3, 5, 6], [False, True, True]),      # (x3 OR NOT x5 OR NOT x6)
        ([0, 2, 5], [True, True, False]),      # (NOT x0 OR NOT x2 OR x5)
        ([0, 2, 7], [False, True, False]),     # (x0 OR NOT x2 OR x7)
        ([0, 3, 7], [False, True, True]),      # (x0 OR NOT x3 OR NOT x7)
        ([1, 3, 5], [True, False, False]),     # (NOT x1 OR x3 OR x5)
        ([0, 2, 3], [False, False, False]),    # (x0 OR x2 OR x3)
        ([0, 1, 3], [False, False, False]),    # (x0 OR x1 OR x3)
    ]
    
    clause_anc = ancilla_qubits[:10]
    temp_anc = ancilla_qubits[10]
    
    # Compute each clause: (l0 OR l1 OR l2) = 1 XOR (NOT l0 AND NOT l1 AND NOT l2)
    for idx, (vars, negs) in enumerate(clauses):
        c = clause_anc[idx]
        q = [problem_qubits[v] for v in vars]
        
        # Initialize c to 1
        qc.x(c)
        
        # Flip for non-negated literals to get NOT literals
        for i, neg in enumerate(negs):
            if not neg:
                qc.x(q[i])
        
        # Compute AND of (NOT l0, NOT l1, NOT l2) using Toffoli gates
        qc.ccx(q[0], q[1], temp_anc)
        qc.ccx(temp_anc, q[2], c)
        qc.ccx(q[0], q[1], temp_anc)
        
        # Unflip to restore problem qubits
        for i, neg in enumerate(negs):
            if not neg:
                qc.x(q[i])
    
    # Compute AND of all clauses: temp_anc = clause_anc[0] AND clause_anc[1] AND ... AND clause_anc[9]
    qc.mcx(clause_anc[:10], temp_anc)
    
    # Apply phase: Z gate flips phase iff temp_anc = 1
    qc.z(temp_anc)
    
    # Uncompute the AND
    qc.mcx(clause_anc[:10], temp_anc)
    
    # Uncompute clauses (mirror of compute in reverse order)
    for idx in range(len(clauses) - 1, -1, -1):
        vars, negs = clauses[idx]
        c = clause_anc[idx]
        q = [problem_qubits[v] for v in vars]
        
        # Flip for non-negated literals
        for i, neg in enumerate(negs):
            if not neg:
                qc.x(q[i])
        
        # Reverse Toffoli sequence
        qc.ccx(q[0], q[1], temp_anc)
        qc.ccx(temp_anc, q[2], c)
        qc.ccx(q[0], q[1], temp_anc)
        
        # Unflip
        for i, neg in enumerate(negs):
            if not neg:
                qc.x(q[i])
        
        # Restore c to 0
        qc.x(c)
