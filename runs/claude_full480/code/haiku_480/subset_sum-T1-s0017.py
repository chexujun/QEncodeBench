import math

def build_oracle(qc, problem_qubits, ancilla_qubits):
    x0, x1, x2 = problem_qubits[0], problem_qubits[1], problem_qubits[2]
    a, b = ancilla_qubits[0], ancilla_qubits[1]
    
    # Compute a = x0 AND x1
    qc.ccx(x0, x1, a)
    
    # Flip x2 to get NOT x2
    qc.x(x2)
    
    # Compute b = a AND x2 (which is x0 AND x1 AND NOT original x2)
    qc.ccx(a, x2, b)
    
    # Apply phase
    qc.p(math.pi, b)
    
    # Uncompute b = a AND x2
    qc.ccx(a, x2, b)
    
    # Flip x2 back
    qc.x(x2)
    
    # Uncompute a = x0 AND x1
    qc.ccx(x0, x1, a)
