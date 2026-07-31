from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x = problem_qubits  # x[0:5]
    a = ancilla_qubits  # a[0:7]
    
    # ===== COMPUTE =====
    
    # Step 1: Compute edge coverage flags (a[0:4])
    # a[0] = x[0] OR x[1]
    qc.cx(x[0], a[0])
    qc.cx(x[1], a[0])
    qc.ccx(x[0], x[1], a[0])
    
    # a[1] = x[1] OR x[2]
    qc.cx(x[1], a[1])
    qc.cx(x[2], a[1])
    qc.ccx(x[1], x[2], a[1])
    
    # a[2] = x[2] OR x[4]
    qc.cx(x[2], a[2])
    qc.cx(x[4], a[2])
    qc.ccx(x[2], x[4], a[2])
    
    # a[3] = x[3] OR x[4]
    qc.cx(x[3], a[3])
    qc.cx(x[4], a[3])
    qc.ccx(x[3], x[4], a[3])
    
    # Step 2: Compute popcount >= 3 into a[5]
    three_tuples = [
        (0, 1, 2), (0, 1, 3), (0, 1, 4),
        (0, 2, 3), (0, 2, 4), (0, 3, 4),
        (1, 2, 3), (1, 2, 4), (1, 3, 4),
        (2, 3, 4)
    ]
    
    for i0, i1, i2 in three_tuples:
        qc.ccx(x[i0], x[i1], a[6])     # a[6] = x[i0] AND x[i1]
        qc.ccx(a[6], x[i2], a[5])      # a[5] = a[5] OR (x[i0] AND x[i1] AND x[i2])
        qc.ccx(x[i0], x[i1], a[6])     # Uncompute a[6]
    
    # Negate: a[5] = NOT(popcount >= 3) = popcount <= 2
    qc.x(a[5])
    
    # Step 3: AND all conditions: edges_ok AND size_ok
    qc.mcx([a[0], a[1], a[2], a[3], a[5]], a[4])
    
    # ===== PHASE =====
    qc.z(a[4])
    
    # ===== UNCOMPUTE =====
    
    qc.mcx([a[0], a[1], a[2], a[3], a[5]], a[4])
    
    qc.x(a[5])
    
    for i0, i1, i2 in reversed(three_tuples):
        qc.ccx(x[i0], x[i1], a[6])
        qc.ccx(a[6], x[i2], a[5])
        qc.ccx(x[i0], x[i1], a[6])
    
    qc.ccx(x[3], x[4], a[3])
    qc.cx(x[4], a[3])
    qc.cx(x[3], a[3])
    
    qc.ccx(x[2], x[4], a[2])
    qc.cx(x[4], a[2])
    qc.cx(x[2], a[2])
    
    qc.ccx(x[1], x[2], a[1])
    qc.cx(x[2], a[1])
    qc.cx(x[1], a[1])
    
    qc.ccx(x[0], x[1], a[0])
    qc.cx(x[1], a[0])
    qc.cx(x[0], a[0])
