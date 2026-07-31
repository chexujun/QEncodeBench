from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    p = problem_qubits
    a = ancilla_qubits
    
    # Initialize a[5] = 1 (will be set to 0 if any clause is unsatisfied)
    qc.x(a[5])
    
    # Clause 1: (x0 OR NOT x1 OR x4) = NOT((x0=0) AND (x1=1) AND (x4=0))
    qc.x(p[0])
    qc.x(p[4])
    qc.ccx(p[0], p[1], a[1])
    qc.ccx(a[1], p[4], a[0])
    qc.ccx(a[0], a[5], a[5])
    qc.ccx(a[1], p[4], a[0])
    qc.ccx(p[0], p[1], a[1])
    qc.x(p[0])
    qc.x(p[4])
    
    # Clause 2: (NOT x2 OR NOT x3 OR NOT x4) = NOT((x2=1) AND (x3=1) AND (x4=1))
    qc.ccx(p[2], p[3], a[1])
    qc.ccx(a[1], p[4], a[0])
    qc.ccx(a[0], a[5], a[5])
    qc.ccx(a[1], p[4], a[0])
    qc.ccx(p[2], p[3], a[1])
    
    # Clause 3: (x0 OR NOT x3 OR x4) = NOT((x0=0) AND (x3=1) AND (x4=0))
    qc.x(p[0])
    qc.x(p[4])
    qc.ccx(p[0], p[3], a[1])
    qc.ccx(a[1], p[4], a[0])
    qc.ccx(a[0], a[5], a[5])
    qc.ccx(a[1], p[4], a[0])
    qc.ccx(p[0], p[3], a[1])
    qc.x(p[0])
    qc.x(p[4])
    
    # Clause 4: (x1 OR x2 OR NOT x4) = NOT((x1=0) AND (x2=0) AND (x4=1))
    qc.x(p[1])
    qc.x(p[2])
    qc.ccx(p[1], p[2], a[1])
    qc.ccx(a[1], p[4], a[0])
    qc.ccx(a[0], a[5], a[5])
    qc.ccx(a[1], p[4], a[0])
    qc.ccx(p[1], p[2], a[1])
    qc.x(p[1])
    qc.x(p[2])
    
    # Clause 5: (x0 OR x2 OR NOT x4) = NOT((x0=0) AND (x2=0) AND (x4=1))
    qc.x(p[0])
    qc.x(p[2])
    qc.ccx(p[0], p[2], a[1])
    qc.ccx(a[1], p[4], a[0])
    qc.ccx(a[0], a[5], a[5])
    qc.ccx(a[1], p[4], a[0])
    qc.ccx(p[0], p[2], a[1])
    qc.x(p[0])
    qc.x(p[2])
    
    # Apply phase -1 to marked state (ancilla a[5] = 1)
    qc.z(a[5])
    
    # Uncompute a[5] back to |0>
    qc.x(a[5])
