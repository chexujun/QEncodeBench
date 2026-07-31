from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    p = problem_qubits
    a = ancilla_qubits
    
    # Compute constraint 1: p[0] = 1 AND p[1] = 0
    # Equivalent to p[0] AND NOT p[1]
    qc.x(p[1])
    qc.ccx(p[0], p[1], a[0])
    qc.x(p[1])
    
    # Compute constraint 2: p[2] XNOR p[3] (i.e., p[2] = p[3])
    qc.cx(p[2], a[1])
    qc.cx(p[3], a[1])
    qc.x(a[1])
    
    # Compute constraint 3: p[4] XNOR p[5] (i.e., p[4] = p[5])
    qc.cx(p[4], a[2])
    qc.cx(p[5], a[2])
    qc.x(a[2])
    
    # Compute constraint 4: p[6] = 1 AND p[7] = 0
    # Equivalent to p[6] AND NOT p[7]
    qc.x(p[7])
    qc.ccx(p[6], p[7], a[3])
    qc.x(p[7])
    
    # Compute AND of all four constraints into a[4]
    qc.mcx([a[0], a[1], a[2], a[3]], a[4])
    
    # Apply phase -1 when all constraints are satisfied
    qc.z(a[4])
    
    # Uncompute: reverse all operations in reverse order
    qc.mcx([a[0], a[1], a[2], a[3]], a[4])
    
    # Uncompute constraint 4
    qc.x(p[7])
    qc.ccx(p[6], p[7], a[3])
    qc.x(p[7])
    
    # Uncompute constraint 3
    qc.x(a[2])
    qc.cx(p[5], a[2])
    qc.cx(p[4], a[2])
    
    # Uncompute constraint 2
    qc.x(a[1])
    qc.cx(p[3], a[1])
    qc.cx(p[2], a[1])
    
    # Uncompute constraint 1
    qc.x(p[1])
    qc.ccx(p[0], p[1], a[0])
    qc.x(p[1])
