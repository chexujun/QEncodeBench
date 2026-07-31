from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x = problem_qubits
    a = ancilla_qubits
    
    # Clause 1: (NOT x0 OR NOT x1 OR NOT x2) = NOT(x0 AND x1 AND x2)
    qc.mcx([x[0], x[1], x[2]], a[0], ctrl_state='111')
    qc.x(a[0])
    
    # Clause 2: (NOT x0 OR x1 OR NOT x2) = NOT(x0 AND NOT x1 AND x2)
    qc.mcx([x[0], x[1], x[2]], a[1], ctrl_state='101')
    qc.x(a[1])
    
    # Clause 3: (x0 OR x1 OR NOT x4) = NOT(NOT x0 AND NOT x1 AND x4)
    qc.mcx([x[0], x[1], x[4]], a[2], ctrl_state='001')
    qc.x(a[2])
    
    # Clause 4: (NOT x0 OR x2 OR NOT x3) = NOT(x0 AND NOT x2 AND x3)
    qc.mcx([x[0], x[2], x[3]], a[3], ctrl_state='101')
    qc.x(a[3])
    
    # Compute AND of all four clauses
    qc.mcx([a[0], a[1], a[2], a[3]], a[4])
    
    # Apply phase flip
    qc.z(a[4])
    
    # Uncompute AND
    qc.mcx([a[0], a[1], a[2], a[3]], a[4])
    
    # Uncompute clauses
    qc.x(a[3])
    qc.mcx([x[0], x[2], x[3]], a[3], ctrl_state='101')
    
    qc.x(a[2])
    qc.mcx([x[0], x[1], x[4]], a[2], ctrl_state='001')
    
    qc.x(a[1])
    qc.mcx([x[0], x[1], x[2]], a[1], ctrl_state='101')
    
    qc.x(a[0])
    qc.mcx([x[0], x[1], x[2]], a[0], ctrl_state='111')
