from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    p = problem_qubits
    a = ancilla_qubits
    
    # Compute match0: (s_0 = 0) AND (s_3 = 1)
    # Use (NOT s_0) AND s_3 logic with Toffoli
    qc.x(p[0])
    qc.ccx(p[0], p[3], a[0])
    qc.x(p[0])
    
    # Compute match1: (s_1 = 0) AND (s_4 = 1)
    qc.x(p[1])
    qc.ccx(p[1], p[4], a[1])
    qc.x(p[1])
    
    # Compute a[2] = a[0] OR a[1] using CX and CCX
    # a[0] OR a[1] = (a[0] XOR a[1]) XOR (a[0] AND a[1])
    qc.cx(a[0], a[2])
    qc.cx(a[1], a[2])
    qc.ccx(a[0], a[1], a[2])
    
    # Apply phase -1 when a[2] = 1
    qc.z(a[2])
    
    # Uncompute a[2] = a[0] OR a[1]
    qc.ccx(a[0], a[1], a[2])
    qc.cx(a[1], a[2])
    qc.cx(a[0], a[2])
    
    # Uncompute match1
    qc.x(p[1])
    qc.ccx(p[1], p[4], a[1])
    qc.x(p[1])
    
    # Uncompute match0
    qc.x(p[0])
    qc.ccx(p[0], p[3], a[0])
    qc.x(p[0])
