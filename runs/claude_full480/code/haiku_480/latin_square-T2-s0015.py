from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    p0, p1, p2, p3, p4, p5 = problem_qubits[0:6]
    a = ancilla_qubits
    
    # Check v0 == 1 (code 01): p0=1 AND p1=0
    qc.x(p1)
    qc.ccx(p0, p1, a[0])
    
    # Check v1 == 2 (code 10): p2=0 AND p3=1
    qc.x(p2)
    qc.ccx(p2, p3, a[1])
    
    # Check v2 == 0 (code 00 or 11): p4 == p5
    qc.cx(p4, a[2])
    qc.cx(p5, a[2])
    qc.x(a[2])
    
    # AND all three conditions
    qc.ccx(a[0], a[1], a[3])
    qc.ccx(a[2], a[3], a[4])
    
    # Apply phase if all conditions are met
    qc.z(a[4])
    
    # Uncompute (reverse order)
    qc.ccx(a[2], a[3], a[4])
    qc.ccx(a[0], a[1], a[3])
    qc.x(a[2])
    qc.cx(p5, a[2])
    qc.cx(p4, a[2])
    qc.x(p2)
    qc.ccx(p2, p3, a[1])
    qc.x(p1)
    qc.ccx(p0, p1, a[0])
