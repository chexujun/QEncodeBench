from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x = problem_qubits
    a = ancilla_qubits
    
    result = a[6]
    
    # COMPUTE
    qc.x(result)  # result = 1 (formula initially satisfied)
    
    # Clause 1: (NOT x0 OR NOT x1 OR NOT x2) - FALSE iff x0 AND x1 AND x2
    qc.ccx(x[0], x[1], a[0])
    qc.ccx(a[0], x[2], a[1])
    qc.x(a[2])
    qc.ccx(a[1], a[2], result)
    qc.x(a[2])
    qc.ccx(a[0], x[2], a[1])
    qc.ccx(x[0], x[1], a[0])
    
    # Clause 2: (x0 OR NOT x1 OR NOT x3) - FALSE iff (NOT x0) AND x1 AND x3
    qc.x(a[0])
    qc.cx(x[0], a[0])
    qc.ccx(a[0], x[1], a[1])
    qc.ccx(a[1], x[3], a[2])
    qc.x(a[3])
    qc.ccx(a[2], a[3], result)
    qc.x(a[3])
    qc.ccx(a[1], x[3], a[2])
    qc.ccx(a[0], x[1], a[1])
    qc.cx(x[0], a[0])
    qc.x(a[0])
    
    # Clause 3: (NOT x0 OR x2 OR NOT x3) - FALSE iff x0 AND (NOT x2) AND x3
    qc.x(a[0])
    qc.cx(x[2], a[0])
    qc.ccx(x[0], a[0], a[1])
    qc.ccx(a[1], x[3], a[2])
    qc.x(a[3])
    qc.ccx(a[2], a[3], result)
    qc.x(a[3])
    qc.ccx(a[1], x[3], a[2])
    qc.ccx(x[0], a[0], a[1])
    qc.cx(x[2], a[0])
    qc.x(a[0])
    
    # Clause 4: (NOT x0 OR x1 OR NOT x3) - FALSE iff x0 AND (NOT x1) AND x3
    qc.x(a[0])
    qc.cx(x[1], a[0])
    qc.ccx(x[0], a[0], a[1])
    qc.ccx(a[1], x[3], a[2])
    qc.x(a[3])
    qc.ccx(a[2], a[3], result)
    qc.x(a[3])
    qc.ccx(a[1], x[3], a[2])
    qc.ccx(x[0], a[0], a[1])
    qc.cx(x[1], a[0])
    qc.x(a[0])
    
    # Clause 5: (NOT x1 OR x2 OR NOT x3) - FALSE iff x1 AND (NOT x2) AND x3
    qc.x(a[0])
    qc.cx(x[2], a[0])
    qc.ccx(x[1], a[0], a[1])
    qc.ccx(a[1], x[3], a[2])
    qc.x(a[3])
    qc.ccx(a[2], a[3], result)
    qc.x(a[3])
    qc.ccx(a[1], x[3], a[2])
    qc.ccx(x[1], a[0], a[1])
    qc.cx(x[2], a[0])
    qc.x(a[0])
    
    # Clause 6: (NOT x0 OR NOT x2 OR x3) - FALSE iff x0 AND x2 AND (NOT x3)
    qc.ccx(x[0], x[2], a[0])
    qc.x(a[1])
    qc.cx(x[3], a[1])
    qc.ccx(a[0], a[1], a[2])
    qc.x(a[3])
    qc.ccx(a[2], a[3], result)
    qc.x(a[3])
    qc.ccx(a[0], a[1], a[2])
    qc.cx(x[3], a[1])
    qc.x(a[1])
    qc.ccx(x[0], x[2], a[0])
    
    # PHASE
    qc.z(result)
    
    # UNCOMPUTE (reverse order)
    # Clause 6
    qc.ccx(x[0], x[2], a[0])
    qc.x(a[1])
    qc.cx(x[3], a[1])
    qc.ccx(a[0], a[1], a[2])
    qc.x(a[3])
    qc.ccx(a[2], a[3], result)
    qc.x(a[3])
    qc.ccx(a[0], a[1], a[2])
    qc.cx(x[3], a[1])
    qc.x(a[1])
    qc.ccx(x[0], x[2], a[0])
    
    # Clause 5
    qc.x(a[0])
    qc.cx(x[2], a[0])
    qc.ccx(x[1], a[0], a[1])
    qc.ccx(a[1], x[3], a[2])
    qc.x(a[3])
    qc.ccx(a[2], a[3], result)
    qc.x(a[3])
    qc.ccx(a[1], x[3], a[2])
    qc.ccx(x[1], a[0], a[1])
    qc.cx(x[2], a[0])
    qc.x(a[0])
    
    # Clause 4
    qc.x(a[0])
    qc.cx(x[1], a[0])
    qc.ccx(x[0], a[0], a[1])
    qc.ccx(a[1], x[3], a[2])
    qc.x(a[3])
    qc.ccx(a[2], a[3], result)
    qc.x(a[3])
    qc.ccx(a[1], x[3], a[2])
    qc.ccx(x[0], a[0], a[1])
    qc.cx(x[1], a[0])
    qc.x(a[0])
    
    # Clause 3
    qc.x(a[0])
    qc.cx(x[2], a[0])
    qc.ccx(x[0], a[0], a[1])
    qc.ccx(a[1], x[3], a[2])
    qc.x(a[3])
    qc.ccx(a[2], a[3], result)
    qc.x(a[3])
    qc.ccx(a[1], x[3], a[2])
    qc.ccx(x[0], a[0], a[1])
    qc.cx(x[2], a[0])
    qc.x(a[0])
    
    # Clause 2
    qc.x(a[0])
    qc.cx(x[0], a[0])
    qc.ccx(a[0], x[1], a[1])
    qc.ccx(a[1], x[3], a[2])
    qc.x(a[3])
    qc.ccx(a[2], a[3], result)
    qc.x(a[3])
    qc.ccx(a[1], x[3], a[2])
    qc.ccx(a[0], x[1], a[1])
    qc.cx(x[0], a[0])
    qc.x(a[0])
    
    # Clause 1
    qc.ccx(x[0], x[1], a[0])
    qc.ccx(a[0], x[2], a[1])
    qc.x(a[2])
    qc.ccx(a[1], a[2], result)
    qc.x(a[2])
    qc.ccx(a[0], x[2], a[1])
    qc.ccx(x[0], x[1], a[0])
    
    qc.x(result)  # Restore result to 0
