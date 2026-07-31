from qiskit import QuantumCircuit

def build_oracle(qc, problem_qubits, ancilla_qubits):
    x = problem_qubits
    a = ancilla_qubits
    
    def compute_or(q_a, q_b, q_result):
        """Compute q_result = q_a OR q_b, assuming q_result starts at |0>"""
        qc.x(q_a)
        qc.x(q_b)
        qc.ccx(q_a, q_b, q_result)
        qc.x(q_result)
        qc.x(q_a)
        qc.x(q_b)
    
    def uncompute_or(q_a, q_b, q_result):
        """Undo compute_or"""
        qc.x(q_a)
        qc.x(q_b)
        qc.x(q_result)
        qc.ccx(q_a, q_b, q_result)
        qc.x(q_b)
        qc.x(q_a)
    
    # === COMPUTE ===
    
    # Compute size constraint: a[4] = 1 iff popcount <= 2
    # Compute the 3-way ANDs
    qc.ccx(x[0], x[1], a[0])
    qc.ccx(a[0], x[2], a[0])
    
    qc.ccx(x[0], x[1], a[1])
    qc.ccx(a[1], x[3], a[1])
    
    qc.ccx(x[0], x[2], a[2])
    qc.ccx(a[2], x[3], a[2])
    
    qc.ccx(x[1], x[2], a[3])
    qc.ccx(a[3], x[3], a[3])
    
    # Compute NOR(a[0], a[1], a[2], a[3])
    qc.x(a[0])
    qc.x(a[1])
    qc.x(a[2])
    qc.x(a[3])
    qc.ccx(a[0], a[1], a[4])
    qc.ccx(a[4], a[2], a[4])
    qc.ccx(a[4], a[3], a[4])
    qc.x(a[3])
    qc.x(a[2])
    qc.x(a[1])
    qc.x(a[0])
    
    # Uncompute the 3-way ANDs
    qc.ccx(x[1], x[2], a[3])
    qc.ccx(a[3], x[3], a[3])
    
    qc.ccx(x[0], x[2], a[2])
    qc.ccx(a[2], x[3], a[2])
    
    qc.ccx(x[0], x[1], a[1])
    qc.ccx(a[1], x[3], a[1])
    
    qc.ccx(x[0], x[1], a[0])
    qc.ccx(a[0], x[2], a[0])
    
    # Compute edge coverage: a[5] = 1 iff all edges are covered
    qc.x(a[5])
    
    compute_or(x[0], x[1], a[0])
    qc.ccx(a[5], a[0], a[5])
    uncompute_or(x[0], x[1], a[0])
    
    compute_or(x[0], x[2], a[0])
    qc.ccx(a[5], a[0], a[5])
    uncompute_or(x[0], x[2], a[0])
    
    compute_or(x[0], x[3], a[0])
    qc.ccx(a[5], a[0], a[5])
    uncompute_or(x[0], x[3], a[0])
    
    compute_or(x[1], x[2], a[0])
    qc.ccx(a[5], a[0], a[5])
    uncompute_or(x[1], x[2], a[0])
    
    compute_or(x[1], x[3], a[0])
    qc.ccx(a[5], a[0], a[5])
    uncompute_or(x[1], x[3], a[0])
    
    # Compute final AND: a[6] = a[4] AND a[5]
    qc.ccx(a[4], a[5], a[6])
    
    # === PHASE ===
    qc.z(a[6])
    
    # === UNCOMPUTE ===
    
    qc.ccx(a[4], a[5], a[6])
    
    compute_or(x[1], x[3], a[0])
    qc.ccx(a[5], a[0], a[5])
    uncompute_or(x[1], x[3], a[0])
    
    compute_or(x[1], x[2], a[0])
    qc.ccx(a[5], a[0], a[5])
    uncompute_or(x[1], x[2], a[0])
    
    compute_or(x[0], x[3], a[0])
    qc.ccx(a[5], a[0], a[5])
    uncompute_or(x[0], x[3], a[0])
    
    compute_or(x[0], x[2], a[0])
    qc.ccx(a[5], a[0], a[5])
    uncompute_or(x[0], x[2], a[0])
    
    compute_or(x[0], x[1], a[0])
    qc.ccx(a[5], a[0], a[5])
    uncompute_or(x[0], x[1], a[0])
    
    qc.x(a[5])
    
    qc.ccx(x[0], x[1], a[0])
    qc.ccx(a[0], x[2], a[0])
    
    qc.ccx(x[0], x[1], a[1])
    qc.ccx(a[1], x[3], a[1])
    
    qc.ccx(x[0], x[2], a[2])
    qc.ccx(a[2], x[3], a[2])
    
    qc.ccx(x[1], x[2], a[3])
    qc.ccx(a[3], x[3], a[3])
    
    qc.x(a[0])
    qc.x(a[1])
    qc.x(a[2])
    qc.x(a[3])
    qc.ccx(a[0], a[1], a[4])
    qc.ccx(a[4], a[2], a[4])
    qc.ccx(a[4], a[3], a[4])
    qc.x(a[3])
    qc.x(a[2])
    qc.x(a[1])
    qc.x(a[0])
    
    qc.ccx(x[1], x[2], a[3])
    qc.ccx(a[3], x[3], a[3])
    
    qc.ccx(x[0], x[2], a[2])
    qc.ccx(a[2], x[3], a[2])
    
    qc.ccx(x[0], x[1], a[1])
    qc.ccx(a[1], x[3], a[1])
    
    qc.ccx(x[0], x[1], a[0])
    qc.ccx(a[0], x[2], a[0])
