import math

def build_oracle(qc, problem_qubits, ancilla_qubits):
    x = problem_qubits
    a = ancilla_qubits
    
    # Compute the violation flags into ancillas
    # a[0]: 1 if x0 != x1 (constraint x0 = x1 violated)
    qc.cx(x[0], a[0])
    qc.cx(x[1], a[0])
    
    # a[1]: 1 if x2 != 0 (constraint x2 = 0 violated)
    qc.cx(x[2], a[1])
    
    # a[2]: 1 if x3 != 1 (constraint x3 = 1 violated)
    qc.x(x[3])
    qc.cx(x[3], a[2])
    qc.x(x[3])
    
    # a[3]: 1 if x4 != x5 (constraint x4 = x5 violated)
    qc.cx(x[4], a[3])
    qc.cx(x[5], a[3])
    
    # a[4]: 1 if x6 != 1 (constraint x6 = 1 violated)
    qc.x(x[6])
    qc.cx(x[6], a[4])
    qc.x(x[6])
    
    # a[5]: 1 if x7 != 0 (constraint x7 = 0 violated)
    qc.cx(x[7], a[5])
    
    # Flip all ancillas so they're 1 when all constraints are satisfied
    for i in range(6):
        qc.x(a[i])
    
    # Apply phase -1 when all ancillas are 1 (all constraints satisfied)
    qc.mcp(math.pi, a[0:5], a[5])
    
    # Unflip the ancillas
    for i in range(6):
        qc.x(a[i])
    
    # Uncompute (mirror of compute)
    qc.cx(x[7], a[5])
    
    qc.x(x[6])
    qc.cx(x[6], a[4])
    qc.x(x[6])
    
    qc.cx(x[5], a[3])
    qc.cx(x[4], a[3])
    
    qc.x(x[3])
    qc.cx(x[3], a[2])
    qc.x(x[3])
    
    qc.cx(x[2], a[1])
    
    qc.cx(x[1], a[0])
    qc.cx(x[0], a[0])
