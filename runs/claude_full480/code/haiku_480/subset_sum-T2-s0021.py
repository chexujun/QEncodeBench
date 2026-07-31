from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x = problem_qubits
    a = ancilla_qubits
    
    # Subset sum: mark x where 7*x[0] + 6*x[1] + 3*x[2] + 3*x[3] = 12
    # Only solution: x[0]=0, x[1]=1, x[2]=1, x[3]=1
    # This means: (NOT x[0]) AND x[1] AND x[2] AND x[3]
    
    # Compute x[1] AND x[2] into a[0]
    qc.ccx(x[1], x[2], a[0])
    
    # Compute (a[0]) AND x[3] into a[1]
    qc.ccx(a[0], x[3], a[1])
    
    # Compute NOT x[0] into a[2]
    qc.cx(x[0], a[2])
    qc.x(a[2])
    
    # Compute (a[2]) AND (a[1]) into a[3]
    qc.ccx(a[2], a[1], a[3])
    
    # Apply phase -1
    qc.z(a[3])
    
    # Uncompute (reverse order)
    qc.ccx(a[2], a[1], a[3])
    qc.x(a[2])
    qc.cx(x[0], a[2])
    qc.ccx(a[0], x[3], a[1])
    qc.ccx(x[1], x[2], a[0])
