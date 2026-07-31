from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x = problem_qubits
    a = ancilla_qubits
    
    # Compute x[0] XOR x[2] into a[0]
    qc.cx(x[0], a[0])
    qc.cx(x[2], a[0])
    
    # Compute NOT x[3] into a[1]
    qc.cx(x[3], a[1])
    qc.x(a[1])
    
    # Compute x[1] AND a[0] into a[2]
    qc.ccx(x[1], a[0], a[2])
    
    # Compute a[2] AND a[1] into a[3] (final predicate)
    qc.ccx(a[2], a[1], a[3])
    
    # Apply phase flip to marked states
    qc.z(a[3])
    
    # Uncompute (reverse order)
    qc.ccx(a[2], a[1], a[3])
    qc.ccx(x[1], a[0], a[2])
    qc.x(a[1])
    qc.cx(x[3], a[1])
    qc.cx(x[2], a[0])
    qc.cx(x[0], a[0])
