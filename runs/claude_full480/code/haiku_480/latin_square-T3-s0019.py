from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    q = problem_qubits
    a = ancilla_qubits
    
    # Compute constraint c0 = q[0] AND NOT q[1]
    qc.x(q[1])
    qc.ccx(q[0], q[1], a[0])
    qc.x(q[1])
    
    # Compute constraint c1 = NOT (q[2] XOR q[3])
    qc.cx(q[2], a[1])
    qc.cx(q[3], a[1])
    qc.x(a[1])
    
    # Compute constraint c2 = q[4] AND NOT q[5]
    qc.x(q[5])
    qc.ccx(q[4], q[5], a[2])
    qc.x(q[5])
    
    # Compute constraint c3 = NOT (q[6] XOR q[7])
    qc.cx(q[6], a[3])
    qc.cx(q[7], a[3])
    qc.x(a[3])
    
    # Compute a[4] = c0 AND c1
    qc.ccx(a[0], a[1], a[4])
    
    # Compute a[5] = c2 AND c3
    qc.ccx(a[2], a[3], a[5])
    
    # Apply phase when all constraints are satisfied
    qc.cz(a[4], a[5])
    
    # Uncompute a[5]
    qc.ccx(a[2], a[3], a[5])
    
    # Uncompute a[4]
    qc.ccx(a[0], a[1], a[4])
    
    # Uncompute constraint c3
    qc.cx(q[6], a[3])
    qc.cx(q[7], a[3])
    qc.x(a[3])
    
    # Uncompute constraint c2
    qc.x(q[5])
    qc.ccx(q[4], q[5], a[2])
    qc.x(q[5])
    
    # Uncompute constraint c1
    qc.cx(q[2], a[1])
    qc.cx(q[3], a[1])
    qc.x(a[1])
    
    # Uncompute constraint c0
    qc.x(q[1])
    qc.ccx(q[0], q[1], a[0])
    qc.x(q[1])
