from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    q = problem_qubits
    a = ancilla_qubits
    
    # Constraint 1: q[0] = 0 AND q[1] = 1
    qc.x(q[0])
    qc.ccx(q[0], q[1], a[0])
    qc.x(q[0])
    
    # Constraint 2: q[2] = 1 AND q[3] = 0
    qc.x(q[3])
    qc.ccx(q[2], q[3], a[1])
    qc.x(q[3])
    
    # Constraint 3: q[4] XNOR q[5]
    # Compute a[3] = NOT q[4]
    qc.x(q[4])
    qc.cx(q[4], a[3])
    qc.x(q[4])
    
    # Compute a[4] = NOT q[5]
    qc.x(q[5])
    qc.cx(q[5], a[4])
    qc.x(q[5])
    
    # Compute a[5] = (NOT q[4]) AND (NOT q[5])
    qc.ccx(a[3], a[4], a[5])
    
    # Compute a[6] = q[4] AND q[5]
    qc.ccx(q[4], q[5], a[6])
    
    # Compute a[2] = a[5] OR a[6] via a[2] = NOT ((NOT a[5]) AND (NOT a[6]))
    qc.x(a[5])
    qc.cx(a[5], a[7])
    qc.x(a[5])
    
    qc.x(a[6])
    qc.cx(a[6], a[8])
    qc.x(a[6])
    
    qc.ccx(a[7], a[8], a[2])
    qc.x(a[2])
    
    # Uncompute a[7], a[8]
    qc.x(a[6])
    qc.cx(a[6], a[8])
    qc.x(a[6])
    
    qc.x(a[5])
    qc.cx(a[5], a[7])
    qc.x(a[5])
    
    # Uncompute a[5], a[6]
    qc.ccx(q[4], q[5], a[6])
    qc.ccx(a[3], a[4], a[5])
    
    # Uncompute a[3], a[4]
    qc.x(q[5])
    qc.cx(q[5], a[4])
    qc.x(q[5])
    
    qc.x(q[4])
    qc.cx(q[4], a[3])
    qc.x(q[4])
    
    # Final: a[9] = a[0] AND a[1], a[10] = a[9] AND a[2]
    qc.ccx(a[0], a[1], a[9])
    qc.ccx(a[9], a[2], a[10])
    
    # Phase flip
    qc.z(a[10])
    
    # Uncompute final
    qc.ccx(a[9], a[2], a[10])
    qc.ccx(a[0], a[1], a[9])
    
    # Uncompute constraints
    qc.x(q[3])
    qc.ccx(q[2], q[3], a[1])
    qc.x(q[3])
    
    qc.x(q[0])
    qc.ccx(q[0], q[1], a[0])
    qc.x(q[0])
