from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    q0, q1, q2, q3 = problem_qubits
    a0, a1, a2, a3, a4 = ancilla_qubits
    
    # Compute: which clauses are false
    
    # Clause 0: (NOT x0 OR NOT x1 OR NOT x3) is false when x0=1, x1=1, x3=1
    qc.mcx([q0, q1, q3], a0)
    
    # Clause 1: (x1 OR NOT x2 OR NOT x3) is false when x1=0, x2=1, x3=1
    qc.x(q1)
    qc.mcx([q1, q2, q3], a1)
    qc.x(q1)
    
    # Clause 2: (x0 OR NOT x1 OR x3) is false when x0=0, x1=1, x3=0
    qc.x(q0)
    qc.x(q3)
    qc.mcx([q0, q1, q3], a2)
    qc.x(q0)
    qc.x(q3)
    
    # Clause 3: (x0 OR x2 OR NOT x3) is false when x0=0, x2=0, x3=1
    qc.x(q0)
    qc.x(q2)
    qc.mcx([q0, q2, q3], a3)
    qc.x(q0)
    qc.x(q2)
    
    # Compute: a4 = NOT(a0 OR a1 OR a2 OR a3) = all clauses satisfied
    # Using De Morgan: NOT(OR) = AND of NOTs
    qc.x(a0)
    qc.x(a1)
    qc.x(a2)
    qc.x(a3)
    qc.mcx([a0, a1, a2, a3], a4)
    qc.x(a0)
    qc.x(a1)
    qc.x(a2)
    qc.x(a3)
    
    # Phase: apply -1 when a4 = 1 (all clauses satisfied)
    qc.z(a4)
    
    # Uncompute: mirror the OR computation
    qc.x(a0)
    qc.x(a1)
    qc.x(a2)
    qc.x(a3)
    qc.mcx([a0, a1, a2, a3], a4)
    qc.x(a0)
    qc.x(a1)
    qc.x(a2)
    qc.x(a3)
    
    # Uncompute clause 3
    qc.x(q0)
    qc.x(q2)
    qc.mcx([q0, q2, q3], a3)
    qc.x(q0)
    qc.x(q2)
    
    # Uncompute clause 2
    qc.x(q0)
    qc.x(q3)
    qc.mcx([q0, q1, q3], a2)
    qc.x(q0)
    qc.x(q3)
    
    # Uncompute clause 1
    qc.x(q1)
    qc.mcx([q1, q2, q3], a1)
    qc.x(q1)
    
    # Uncompute clause 0
    qc.mcx([q0, q1, q3], a0)
