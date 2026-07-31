from qiskit import QuantumCircuit

def build_oracle(qc, problem_qubits, ancilla_qubits):
    x = problem_qubits
    a = ancilla_qubits
    
    # State 0011: x[0]=1, x[1]=1, x[2]=0, x[3]=0
    qc.ccx(x[0], x[1], a[0])
    qc.x(x[2])
    qc.ccx(a[0], x[2], a[1])
    qc.x(x[2])
    qc.x(x[3])
    qc.ccx(a[1], x[3], a[2])
    qc.x(x[3])
    qc.z(a[2])
    qc.x(x[3])
    qc.ccx(a[1], x[3], a[2])
    qc.x(x[3])
    qc.x(x[2])
    qc.ccx(a[0], x[2], a[1])
    qc.x(x[2])
    qc.ccx(x[0], x[1], a[0])
    
    # State 1010: x[0]=0, x[1]=1, x[2]=0, x[3]=1
    qc.x(x[0])
    qc.ccx(x[0], x[1], a[0])
    qc.x(x[0])
    qc.x(x[2])
    qc.ccx(a[0], x[2], a[1])
    qc.x(x[2])
    qc.ccx(a[1], x[3], a[2])
    qc.z(a[2])
    qc.ccx(a[1], x[3], a[2])
    qc.x(x[2])
    qc.ccx(a[0], x[2], a[1])
    qc.x(x[2])
    qc.x(x[0])
    qc.ccx(x[0], x[1], a[0])
    qc.x(x[0])
    
    # State 1100: x[0]=0, x[1]=0, x[2]=1, x[3]=1
    qc.x(x[0])
    qc.x(x[1])
    qc.ccx(x[0], x[1], a[0])
    qc.x(x[1])
    qc.x(x[0])
    qc.ccx(a[0], x[2], a[1])
    qc.ccx(a[1], x[3], a[2])
    qc.z(a[2])
    qc.ccx(a[1], x[3], a[2])
    qc.ccx(a[0], x[2], a[1])
    qc.x(x[0])
    qc.x(x[1])
    qc.ccx(x[0], x[1], a[0])
    qc.x(x[1])
    qc.x(x[0])
