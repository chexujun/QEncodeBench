from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x = problem_qubits  # x[0], x[1], x[2], x[3]
    a = ancilla_qubits  # a[0], a[1], a[2], a[3], a[4], a[5]
    
    # Compute x[0] AND x[2] into a[0]
    qc.ccx(x[0], x[2], a[0])
    
    # Compute x[0] AND x[3] into a[1]
    qc.ccx(x[0], x[3], a[1])
    
    # Compute x[2] AND x[3] into a[2]
    qc.ccx(x[2], x[3], a[2])
    
    # Compute OR(a[0], a[1], a[3])
    qc.cx(a[0], a[3])
    qc.cx(a[1], a[3])
    qc.ccx(a[0], a[1], a[3])
    
    # Compute OR(a[3], a[2], a[4])
    qc.cx(a[3], a[4])
    qc.cx(a[2], a[4])
    qc.ccx(a[3], a[2], a[4])
    
    # Now a[4] = (x[0] AND x[2]) OR (x[0] AND x[3]) OR (x[2] AND x[3])
    
    # Compute mark = x[1] AND NOT(a[4])
    qc.x(a[4])  # a[4] = NOT(a[4])
    qc.ccx(x[1], a[4], a[5])  # a[5] = x[1] AND a[4]
    qc.x(a[4])  # a[4] = original a[4]
    
    # Apply Z gate to a[5]
    qc.z(a[5])
    
    # Uncompute mark
    qc.x(a[4])
    qc.ccx(x[1], a[4], a[5])
    qc.x(a[4])
    
    # Uncompute OR(a[3], a[2], a[4])
    qc.ccx(a[3], a[2], a[4])
    qc.cx(a[2], a[4])
    qc.cx(a[3], a[4])
    
    # Uncompute OR(a[0], a[1], a[3])
    qc.ccx(a[0], a[1], a[3])
    qc.cx(a[1], a[3])
    qc.cx(a[0], a[3])
    
    # Uncompute x[2] AND x[3] from a[2]
    qc.ccx(x[2], x[3], a[2])
    
    # Uncompute x[0] AND x[3] from a[1]
    qc.ccx(x[0], x[3], a[1])
    
    # Uncompute x[0] AND x[2] from a[0]
    qc.ccx(x[0], x[2], a[0])
