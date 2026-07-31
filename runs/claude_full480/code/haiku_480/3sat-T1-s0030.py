from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x = problem_qubits
    a = ancilla_qubits
    
    def compute_3and(qc, ctrl1, ctrl2, ctrl3, out, helper):
        """Compute out = out XOR (ctrl1 AND ctrl2 AND ctrl3)"""
        qc.ccx(ctrl1, ctrl2, helper)
        qc.ccx(helper, ctrl3, out)
        qc.ccx(ctrl1, ctrl2, helper)
    
    # Compute each clause into a[0-4]
    # Clause 1: (x0 OR NOT x1 OR NOT x3) - FALSE when (x0=0, x1=1, x3=1)
    qc.x(x[0])
    qc.x(x[3])
    compute_3and(qc, x[0], x[1], x[3], a[0], a[5])
    qc.x(x[0])
    qc.x(x[3])
    qc.x(a[0])
    
    # Clause 2: (x0 OR x1 OR NOT x3) - FALSE when (x0=0, x1=0, x3=1)
    qc.x(x[0])
    qc.x(x[1])
    qc.x(x[3])
    compute_3and(qc, x[0], x[1], x[3], a[1], a[5])
    qc.x(x[0])
    qc.x(x[1])
    qc.x(x[3])
    qc.x(a[1])
    
    # Clause 3: (x1 OR x2 OR x3) - FALSE when (x1=0, x2=0, x3=0)
    qc.x(x[1])
    qc.x(x[2])
    qc.x(x[3])
    compute_3and(qc, x[1], x[2], x[3], a[2], a[5])
    qc.x(x[1])
    qc.x(x[2])
    qc.x(x[3])
    qc.x(a[2])
    
    # Clause 4: (NOT x0 OR NOT x1 OR x3) - FALSE when (x0=1, x1=1, x3=0)
    qc.x(x[3])
    compute_3and(qc, x[0], x[1], x[3], a[3], a[5])
    qc.x(x[3])
    qc.x(a[3])
    
    # Clause 5: (NOT x0 OR NOT x1 OR x2) - FALSE when (x0=1, x1=1, x2=0)
    qc.x(x[2])
    compute_3and(qc, x[0], x[1], x[2], a[4], a[5])
    qc.x(x[2])
    qc.x(a[4])
    
    # Compute AND of all clauses into a[5]
    qc.mcx([a[0], a[1], a[2], a[3], a[4]], a[5])
    
    # Apply phase flip
    qc.z(a[5])
    
    # Uncompute AND
    qc.mcx([a[0], a[1], a[2], a[3], a[4]], a[5])
    
    # Uncompute each clause (reverse order)
    # Clause 5
    qc.x(a[4])
    qc.x(x[2])
    compute_3and(qc, x[0], x[1], x[2], a[4], a[5])
    qc.x(x[2])
    
    # Clause 4
    qc.x(a[3])
    qc.x(x[3])
    compute_3and(qc, x[0], x[1], x[3], a[3], a[5])
    qc.x(x[3])
    
    # Clause 3
    qc.x(a[2])
    qc.x(x[1])
    qc.x(x[2])
    qc.x(x[3])
    compute_3and(qc, x[1], x[2], x[3], a[2], a[5])
    qc.x(x[1])
    qc.x(x[2])
    qc.x(x[3])
    
    # Clause 2
    qc.x(a[1])
    qc.x(x[0])
    qc.x(x[1])
    qc.x(x[3])
    compute_3and(qc, x[0], x[1], x[3], a[1], a[5])
    qc.x(x[0])
    qc.x(x[1])
    qc.x(x[3])
    
    # Clause 1
    qc.x(a[0])
    qc.x(x[0])
    qc.x(x[3])
    compute_3and(qc, x[0], x[1], x[3], a[0], a[5])
    qc.x(x[0])
    qc.x(x[3])
