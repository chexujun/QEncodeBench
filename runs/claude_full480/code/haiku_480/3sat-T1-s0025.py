from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    p = problem_qubits
    a = ancilla_qubits
    
    # Initialize result register to 1
    qc.x(a[0])
    
    # Process each clause by computing AND sequentially
    # Clause 1: (NOT x0 OR x1 OR NOT x2)
    _compute_clause_1_and(qc, p, a)
    
    # Clause 2: (NOT x0 OR NOT x1 OR NOT x2)
    _compute_clause_2_and(qc, p, a)
    
    # Clause 3: (NOT x0 OR x1 OR x2)
    _compute_clause_3_and(qc, p, a)
    
    # Clause 4: (x0 OR x1 OR NOT x2)
    _compute_clause_4_and(qc, p, a)
    
    # Apply phase to result
    qc.z(a[0])
    
    # Uncompute clauses in reverse order
    _uncompute_clause_4_and(qc, p, a)
    _uncompute_clause_3_and(qc, p, a)
    _uncompute_clause_2_and(qc, p, a)
    _uncompute_clause_1_and(qc, p, a)
    
    # Reset result register
    qc.x(a[0])

def _compute_clause_1_and(qc, p, a):
    # Clause 1: NOT(x0 AND NOT x1 AND x2) into a[1], then AND into a[0]
    qc.x(a[1])
    qc.cx(p[1], a[1])  # a[1] = NOT x1
    qc.mcx([p[0], a[1], p[2]], a[2])  # a[2] = x0 AND NOT x1 AND x2
    qc.x(a[2])  # a[2] = clause 1
    qc.ccx(a[2], a[0], a[0])  # a[0] = a[0] AND a[2]

def _uncompute_clause_1_and(qc, p, a):
    qc.x(a[2])
    qc.mcx([p[0], a[1], p[2]], a[2])
    qc.cx(p[1], a[1])
    qc.x(a[1])

def _compute_clause_2_and(qc, p, a):
    # Clause 2: NOT(x0 AND x1 AND x2) into a[1], then AND into a[0]
    qc.mcx([p[0], p[1], p[2]], a[1])  # a[1] = x0 AND x1 AND x2
    qc.x(a[1])  # a[1] = clause 2
    qc.ccx(a[1], a[0], a[0])  # a[0] = a[0] AND a[1]

def _uncompute_clause_2_and(qc, p, a):
    qc.x(a[1])
    qc.mcx([p[0], p[1], p[2]], a[1])

def _compute_clause_3_and(qc, p, a):
    # Clause 3: NOT(x0 AND NOT x1 AND NOT x2) into a[1], then AND into a[0]
    qc.x(a[1])
    qc.cx(p[1], a[1])  # a[1] = NOT x1
    qc.x(a[2])
    qc.cx(p[2], a[2])  # a[2] = NOT x2
    qc.mcx([p[0], a[1], a[2]], a[3])  # a[3] = x0 AND NOT x1 AND NOT x2
    qc.x(a[3])  # a[3] = clause 3
    qc.ccx(a[3], a[0], a[0])  # a[0] = a[0] AND a[3]

def _uncompute_clause_3_and(qc, p, a):
    qc.x(a[3])
    qc.mcx([p[0], a[1], a[2]], a[3])
    qc.cx(p[2], a[2])
    qc.x(a[2])
    qc.cx(p[1], a[1])
    qc.x(a[1])

def _compute_clause_4_and(qc, p, a):
    # Clause 4: NOT(NOT x0 AND NOT x1 AND x2) into a[1], then AND into a[0]
    qc.x(a[1])
    qc.cx(p[0], a[1])  # a[1] = NOT x0
    qc.x(a[2])
    qc.cx(p[1], a[2])  # a[2] = NOT x1
    qc.mcx([a[1], a[2], p[2]], a[3])  # a[3] = NOT x0 AND NOT x1 AND x2
    qc.x(a[3])  # a[3] = clause 4
    qc.ccx(a[3], a[0], a[0])  # a[0] = a[0] AND a[3]

def _uncompute_clause_4_and(qc, p, a):
    qc.x(a[3])
    qc.mcx([a[1], a[2], p[2]], a[3])
    qc.cx(p[1], a[2])
    qc.x(a[2])
    qc.cx(p[0], a[1])
    qc.x(a[1])
