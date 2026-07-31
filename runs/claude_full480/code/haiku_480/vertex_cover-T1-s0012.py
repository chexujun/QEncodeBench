from qiskit import QuantumCircuit

def build_oracle(qc, problem_qubits, ancilla_qubits):
    x = problem_qubits
    a = ancilla_qubits
    
    # Valid vertex covers of size ≤ 2: {0,1} and {1,3}
    # State |0011>: x[0]=1, x[1]=1, x[2]=0, x[3]=0
    # State |1010>: x[0]=0, x[1]=1, x[2]=0, x[3]=1
    
    # Compute first term: x[0] AND x[1] AND NOT x[2] AND NOT x[3] into a[3]
    qc.ccx(x[0], x[1], a[1])
    
    qc.x(a[2])
    qc.x(x[2])
    qc.x(x[3])
    qc.ccx(x[2], x[3], a[2])
    qc.x(x[3])
    qc.x(x[2])
    
    qc.ccx(a[1], a[2], a[3])
    
    # Compute second term: NOT x[0] AND x[1] AND NOT x[2] AND x[3] into a[6]
    qc.x(a[4])
    qc.x(x[0])
    qc.ccx(x[0], x[1], a[4])
    qc.x(x[0])
    
    qc.x(a[5])
    qc.x(x[2])
    qc.ccx(x[2], x[3], a[5])
    qc.x(x[2])
    
    qc.ccx(a[4], a[5], a[6])
    
    # Compute mark = term1 OR term2 into a[0]
    qc.x(a[0])
    qc.x(a[3])
    qc.x(a[6])
    qc.ccx(a[3], a[6], a[0])
    qc.x(a[6])
    qc.x(a[3])
    
    # Phase flip
    qc.z(a[0])
    
    # Uncompute in reverse order
    qc.x(a[3])
    qc.x(a[6])
    qc.ccx(a[3], a[6], a[0])
    qc.x(a[6])
    qc.x(a[3])
    qc.x(a[0])
    
    qc.ccx(a[4], a[5], a[6])
    
    qc.x(x[2])
    qc.ccx(x[2], x[3], a[5])
    qc.x(x[2])
    qc.x(a[5])
    
    qc.x(x[0])
    qc.ccx(x[0], x[1], a[4])
    qc.x(x[0])
    qc.x(a[4])
    
    qc.ccx(a[1], a[2], a[3])
    
    qc.x(x[2])
    qc.x(x[3])
    qc.ccx(x[2], x[3], a[2])
    qc.x(x[3])
    qc.x(x[2])
    qc.x(a[2])
    
    qc.ccx(x[0], x[1], a[1])
