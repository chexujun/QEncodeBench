from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    p = problem_qubits
    a = ancilla_qubits
    
    # Predicate: f(x) = x[0] AND NOT x[1] AND (x[2] XOR x[3])
    # This selects vertex covers {0,2} and {0,3} with size exactly 2
    
    # Compute NOT x[1] into a[1]
    qc.x(a[1])
    qc.cx(p[1], a[1])
    
    # Compute x[2] XOR x[3] into a[2]
    qc.cx(p[2], a[2])
    qc.cx(p[3], a[2])
    
    # Compute x[0] AND NOT x[1] into a[3]
    qc.ccx(p[0], a[1], a[3])
    
    # Compute the final predicate: a[3] AND a[2] into a[0]
    qc.ccx(a[3], a[2], a[0])
    
    # Apply phase flip for marked states
    qc.z(a[0])
    
    # Uncompute: reverse the above operations
    qc.ccx(a[3], a[2], a[0])
    qc.ccx(p[0], a[1], a[3])
    qc.cx(p[3], a[2])
    qc.cx(p[2], a[2])
    qc.cx(p[1], a[1])
    qc.x(a[1])
