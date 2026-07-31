def build_oracle(qc, problem_qubits, ancilla_qubits):
    x = problem_qubits
    a = ancilla_qubits
    
    # Initialize result accumulator to 1
    qc.x(a[5])
    
    # False condition 1: NOT x1 AND x2 AND x3
    qc.x(a[0])
    qc.cx(x[1], a[0])
    qc.ccx(a[0], x[2], a[1])
    qc.ccx(a[1], x[3], a[2])
    qc.x(a[2])
    qc.ccx(a[2], a[5], a[5])
    qc.x(a[2])
    qc.ccx(a[1], x[3], a[2])
    qc.ccx(a[0], x[2], a[1])
    qc.cx(x[1], a[0])
    qc.x(a[0])
    
    # False condition 2: x1 AND NOT x2 AND NOT x3
    qc.cx(x[1], a[0])
    qc.x(a[1])
    qc.cx(x[2], a[1])
    qc.ccx(a[0], a[1], a[2])
    qc.x(a[3])
    qc.cx(x[3], a[3])
    qc.ccx(a[2], a[3], a[4])
    qc.x(a[4])
    qc.ccx(a[4], a[5], a[5])
    qc.x(a[4])
    qc.ccx(a[2], a[3], a[4])
    qc.x(a[3])
    qc.ccx(a[0], a[1], a[2])
    qc.x(a[1])
    qc.cx(x[2], a[1])
    qc.cx(x[1], a[0])
    
    # False condition 3: x0 AND NOT x2 AND NOT x3
    qc.cx(x[0], a[0])
    qc.x(a[1])
    qc.cx(x[2], a[1])
    qc.ccx(a[0], a[1], a[2])
    qc.x(a[3])
    qc.cx(x[3], a[3])
    qc.ccx(a[2], a[3], a[4])
    qc.x(a[4])
    qc.ccx(a[4], a[5], a[5])
    qc.x(a[4])
    qc.ccx(a[2], a[3], a[4])
    qc.x(a[3])
    qc.ccx(a[0], a[1], a[2])
    qc.x(a[1])
    qc.cx(x[2], a[1])
    qc.cx(x[0], a[0])
    
    # False condition 4: NOT x0 AND NOT x1 AND x3
    qc.x(a[0])
    qc.cx(x[0], a[0])
    qc.x(a[1])
    qc.cx(x[1], a[1])
    qc.ccx(a[0], a[1], a[2])
    qc.ccx(a[2], x[3], a[4])
    qc.x(a[4])
    qc.ccx(a[4], a[5], a[5])
    qc.x(a[4])
    qc.ccx(a[2], x[3], a[4])
    qc.ccx(a[0], a[1], a[2])
    qc.x(a[1])
    qc.cx(x[1], a[1])
    qc.x(a[0])
    qc.cx(x[0], a[0])
    
    # False condition 5: x0 AND NOT x2 AND x3
    qc.cx(x[0], a[0])
    qc.x(a[1])
    qc.cx(x[2], a[1])
    qc.ccx(a[0], a[1], a[2])
    qc.ccx(a[2], x[3], a[4])
    qc.x(a[4])
    qc.ccx(a[4], a[5], a[5])
    qc.x(a[4])
    qc.ccx(a[2], x[3], a[4])
    qc.ccx(a[0], a[1], a[2])
    qc.x(a[1])
    qc.cx(x[2], a[1])
    qc.cx(x[0], a[0])
    
    # Apply phase
    qc.z(a[5])
    
    # Reset accumulator
    qc.x(a[5])
