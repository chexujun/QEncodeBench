from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x = problem_qubits
    a = ancilla_qubits
    
    # Compute violation status for each clause into a[0-4]
    # Each clause is violated (false) under specific conditions:
    # C1: x1=1 AND x4=1 AND x5=0
    # C2: x0=0 AND x1=0 AND x4=1
    # C3: x0=0 AND x1=0 AND x5=1
    # C4: x1=0 AND x3=0 AND x5=1
    # C5: x0=1 AND x3=1 AND x5=1
    
    # Clause 1 violation: (x1 AND x4 AND NOT x5)
    qc.x(x[5])
    qc.ccx(x[1], x[4], a[5])
    qc.ccx(a[5], x[5], a[0])
    qc.ccx(x[1], x[4], a[5])
    qc.x(x[5])
    
    # Clause 2 violation: (NOT x0 AND NOT x1 AND x4)
    qc.x(x[0])
    qc.x(x[1])
    qc.ccx(x[0], x[1], a[5])
    qc.ccx(a[5], x[4], a[1])
    qc.ccx(x[0], x[1], a[5])
    qc.x(x[1])
    qc.x(x[0])
    
    # Clause 3 violation: (NOT x0 AND NOT x1 AND x5)
    qc.x(x[0])
    qc.x(x[1])
    qc.ccx(x[0], x[1], a[5])
    qc.ccx(a[5], x[5], a[2])
    qc.ccx(x[0], x[1], a[5])
    qc.x(x[1])
    qc.x(x[0])
    
    # Clause 4 violation: (NOT x1 AND NOT x3 AND x5)
    qc.x(x[1])
    qc.x(x[3])
    qc.ccx(x[1], x[3], a[5])
    qc.ccx(a[5], x[5], a[3])
    qc.ccx(x[1], x[3], a[5])
    qc.x(x[3])
    qc.x(x[1])
    
    # Clause 5 violation: (x0 AND x3 AND x5)
    qc.ccx(x[0], x[3], a[5])
    qc.ccx(a[5], x[5], a[4])
    qc.ccx(x[0], x[3], a[5])
    
    # Flip violation markers to get satisfaction markers
    qc.x(a[0])
    qc.x(a[1])
    qc.x(a[2])
    qc.x(a[3])
    qc.x(a[4])
    
    # Compute AND of all satisfaction markers into a[5], apply phase, uncompute
    qc.mcx([a[0], a[1], a[2], a[3], a[4]], a[5])
    qc.z(a[5])
    qc.mcx([a[0], a[1], a[2], a[3], a[4]], a[5])
    
    # Undo X flips
    qc.x(a[0])
    qc.x(a[1])
    qc.x(a[2])
    qc.x(a[3])
    qc.x(a[4])
    
    # Uncompute violation markers (reverse order)
    qc.ccx(x[0], x[3], a[5])
    qc.ccx(a[5], x[5], a[4])
    qc.ccx(x[0], x[3], a[5])
    
    qc.x(x[1])
    qc.x(x[3])
    qc.ccx(x[1], x[3], a[5])
    qc.ccx(a[5], x[5], a[3])
    qc.ccx(x[1], x[3], a[5])
    qc.x(x[3])
    qc.x(x[1])
    
    qc.x(x[0])
    qc.x(x[1])
    qc.ccx(x[0], x[1], a[5])
    qc.ccx(a[5], x[5], a[2])
    qc.ccx(x[0], x[1], a[5])
    qc.x(x[1])
    qc.x(x[0])
    
    qc.x(x[0])
    qc.x(x[1])
    qc.ccx(x[0], x[1], a[5])
    qc.ccx(a[5], x[4], a[1])
    qc.ccx(x[0], x[1], a[5])
    qc.x(x[1])
    qc.x(x[0])
    
    qc.x(x[5])
    qc.ccx(x[1], x[4], a[5])
    qc.ccx(a[5], x[5], a[0])
    qc.ccx(x[1], x[4], a[5])
    qc.x(x[5])
