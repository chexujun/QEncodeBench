from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    p = problem_qubits
    a = ancilla_qubits
    
    # First solution: bits [1, 0, 0, 1] -> sum = 1 + 7 = 8
    qc.cx(p[1], a[0])
    qc.x(a[0])
    qc.cx(p[2], a[1])
    qc.x(a[1])
    qc.ccx(p[0], a[0], a[2])
    qc.ccx(a[2], a[1], a[3])
    qc.ccx(a[3], p[3], a[4])
    qc.z(a[4])
    qc.ccx(a[3], p[3], a[4])
    qc.ccx(a[2], a[1], a[3])
    qc.ccx(p[0], a[0], a[2])
    qc.x(a[1])
    qc.cx(p[2], a[1])
    qc.x(a[0])
    qc.cx(p[1], a[0])
    
    # Second solution: bits [0, 1, 1, 0] -> sum = 4 + 4 = 8
    qc.cx(p[0], a[0])
    qc.x(a[0])
    qc.cx(p[3], a[1])
    qc.x(a[1])
    qc.ccx(a[0], p[1], a[2])
    qc.ccx(a[2], p[2], a[3])
    qc.ccx(a[3], a[1], a[4])
    qc.z(a[4])
    qc.ccx(a[3], a[1], a[4])
    qc.ccx(a[2], p[2], a[3])
    qc.ccx(a[0], p[1], a[2])
    qc.x(a[1])
    qc.cx(p[3], a[1])
    qc.x(a[0])
    qc.cx(p[0], a[0])
