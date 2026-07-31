import math

def build_oracle(qc, problem_qubits, ancilla_qubits):
    p = problem_qubits
    a = ancilla_qubits
    
    # Compute sum into ancilla
    qc.cx(p[2], a[0])
    qc.cx(p[1], a[1])
    qc.cx(p[0], a[2])
    qc.cx(p[2], a[2])
    qc.mcx([p[0], p[2]], a[3])
    
    # Apply phase if sum == 7
    qc.x(a[3])
    qc.mcp(math.pi, [a[0], a[1], a[2]], a[3])
    qc.x(a[3])
    
    # Uncompute
    qc.mcx([p[0], p[2]], a[3])
    qc.cx(p[2], a[2])
    qc.cx(p[0], a[2])
    qc.cx(p[1], a[1])
    qc.cx(p[2], a[0])
