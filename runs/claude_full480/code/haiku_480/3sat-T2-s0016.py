from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x = problem_qubits
    a = ancilla_qubits
    
    # COMPUTE: evaluate each clause into a[0-5]
    
    # Clause 1: (NOT x0 OR NOT x1 OR x3) = NOT(x0 AND x1 AND NOT x3)
    qc.ccx(x[0], x[1], a[6])
    qc.x(x[3])
    qc.ccx(a[6], x[3], a[0])
    qc.x(x[3])
    qc.ccx(x[0], x[1], a[6])
    qc.x(a[0])
    
    # Clause 2: (x1 OR x4 OR NOT x5) = NOT(NOT x1 AND NOT x4 AND x5)
    qc.x(x[1])
    qc.x(x[4])
    qc.ccx(x[1], x[4], a[6])
    qc.ccx(a[6], x[5], a[1])
    qc.ccx(x[1], x[4], a[6])
    qc.x(x[1])
    qc.x(x[4])
    qc.x(a[1])
    
    # Clause 3: (x1 OR x2 OR x3) = NOT(NOT x1 AND NOT x2 AND NOT x3)
    qc.x(x[1])
    qc.x(x[2])
    qc.x(x[3])
    qc.ccx(x[1], x[2], a[6])
    qc.ccx(a[6], x[3], a[2])
    qc.ccx(x[1], x[2], a[6])
    qc.x(x[1])
    qc.x(x[2])
    qc.x(x[3])
    qc.x(a[2])
    
    # Clause 4: (NOT x0 OR NOT x1 OR NOT x4) = NOT(x0 AND x1 AND x4)
    qc.ccx(x[0], x[1], a[6])
    qc.ccx(a[6], x[4], a[3])
    qc.ccx(x[0], x[1], a[6])
    qc.x(a[3])
    
    # Clause 5: (NOT x0 OR NOT x1 OR NOT x2) = NOT(x0 AND x1 AND x2)
    qc.ccx(x[0], x[1], a[6])
    qc.ccx(a[6], x[2], a[4])
    qc.ccx(x[0], x[1], a[6])
    qc.x(a[4])
    
    # Clause 6: (NOT x1 OR x3 OR NOT x4) = NOT(x1 AND NOT x3 AND x4)
    qc.x(x[3])
    qc.ccx(x[1], x[3], a[6])
    qc.ccx(a[6], x[4], a[5])
    qc.ccx(x[1], x[3], a[6])
    qc.x(x[3])
    qc.x(a[5])
    
    # AND all 6 clauses into a[6]
    qc.mcx([a[0], a[1], a[2], a[3], a[4], a[5]], a[6])
    
    # PHASE: apply Z gate
    qc.z(a[6])
    
    # UNCOMPUTE: reverse all steps
    qc.mcx([a[0], a[1], a[2], a[3], a[4], a[5]], a[6])
    
    # Clause 6
    qc.x(a[5])
    qc.x(x[3])
    qc.ccx(x[1], x[3], a[6])
    qc.ccx(a[6], x[4], a[5])
    qc.ccx(x[1], x[3], a[6])
    qc.x(x[3])
    
    # Clause 5
    qc.x(a[4])
    qc.ccx(x[0], x[1], a[6])
    qc.ccx(a[6], x[2], a[4])
    qc.ccx(x[0], x[1], a[6])
    
    # Clause 4
    qc.x(a[3])
    qc.ccx(x[0], x[1], a[6])
    qc.ccx(a[6], x[4], a[3])
    qc.ccx(x[0], x[1], a[6])
    
    # Clause 3
    qc.x(a[2])
    qc.x(x[1])
    qc.x(x[2])
    qc.x(x[3])
    qc.ccx(x[1], x[2], a[6])
    qc.ccx(a[6], x[3], a[2])
    qc.ccx(x[1], x[2], a[6])
    qc.x(x[1])
    qc.x(x[2])
    qc.x(x[3])
    
    # Clause 2
    qc.x(a[1])
    qc.x(x[1])
    qc.x(x[4])
    qc.ccx(x[1], x[4], a[6])
    qc.ccx(a[6], x[5], a[1])
    qc.ccx(x[1], x[4], a[6])
    qc.x(x[1])
    qc.x(x[4])
    
    # Clause 1
    qc.x(a[0])
    qc.ccx(x[0], x[1], a[6])
    qc.x(x[3])
    qc.ccx(a[6], x[3], a[0])
    qc.x(x[3])
    qc.ccx(x[0], x[1], a[6])
