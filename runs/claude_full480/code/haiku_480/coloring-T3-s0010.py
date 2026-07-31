from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 2), (0, 5), (1, 2), (1, 3), (1, 4), (1, 5), (3, 4)]
    
    acc_anc = ancilla_qubits[0]
    cons_anc = ancilla_qubits[1]
    temp_anc = ancilla_qubits[2]
    
    def add_case(check_bits):
        for q, val in check_bits:
            if not val:
                qc.x(q)
        qc.mcx([q for q, _ in check_bits], temp_anc)
        qc.cx(temp_anc, cons_anc)
        qc.mcx([q for q, _ in check_bits], temp_anc)
        for q, val in check_bits:
            if not val:
                qc.x(q)
    
    def remove_case(check_bits):
        for q, val in check_bits:
            if not val:
                qc.x(q)
        qc.mcx([q for q, _ in check_bits], temp_anc)
        qc.cx(temp_anc, cons_anc)
        qc.mcx([q for q, _ in check_bits], temp_anc)
        for q, val in check_bits:
            if not val:
                qc.x(q)
    
    def edge_gates(u, v):
        u0, u1 = problem_qubits[2*u], problem_qubits[2*u+1]
        v0, v1 = problem_qubits[2*v], problem_qubits[2*v+1]
        
        # Compute OR of 6 "colors_same" cases into cons_anc
        add_case([(u0, 0), (u1, 0), (v0, 0), (v1, 0)])
        add_case([(u0, 0), (u1, 0), (v0, 1), (v1, 1)])
        add_case([(u0, 0), (u1, 1), (v0, 0), (v1, 1)])
        add_case([(u0, 1), (u1, 0), (v0, 1), (v1, 0)])
        add_case([(u0, 1), (u1, 1), (v0, 0), (v1, 0)])
        add_case([(u0, 1), (u1, 1), (v0, 1), (v1, 1)])
        
        # Flip to get colors_different
        qc.x(cons_anc)
        
        # AND with accumulator: acc := acc AND cons
        qc.ccx(acc_anc, cons_anc, temp_anc)
        qc.cx(acc_anc, temp_anc)
        qc.cx(temp_anc, acc_anc)
        qc.cx(acc_anc, temp_anc)
    
    def unedit_edge_gates(u, v):
        u0, u1 = problem_qubits[2*u], problem_qubits[2*u+1]
        v0, v1 = problem_qubits[2*v], problem_qubits[2*v+1]
        
        # Undo AND
        qc.cx(acc_anc, temp_anc)
        qc.cx(temp_anc, acc_anc)
        qc.cx(acc_anc, temp_anc)
        qc.ccx(acc_anc, cons_anc, temp_anc)
        
        # Undo flip
        qc.x(cons_anc)
        
        # Undo colors_same computation (reverse order)
        remove_case([(u0, 1), (u1, 1), (v0, 1), (v1, 1)])
        remove_case([(u0, 1), (u1, 1), (v0, 0), (v1, 0)])
        remove_case([(u0, 1), (u1, 0), (v0, 1), (v1, 0)])
        remove_case([(u0, 0), (u1, 1), (v0, 0), (v1, 1)])
        remove_case([(u0, 0), (u1, 0), (v0, 1), (v1, 1)])
        remove_case([(u0, 0), (u1, 0), (v0, 0), (v1, 0)])
    
    # Compute phase: accumulate AND of all edge constraints
    qc.x(acc_anc)
    for u, v in edges:
        edge_gates(u, v)
    
    # Apply phase flip
    qc.z(acc_anc)
    
    # Uncompute phase: reverse all operations
    for u, v in reversed(edges):
        unedit_edge_gates(u, v)
    qc.x(acc_anc)
