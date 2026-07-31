from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x = problem_qubits  # x[0], x[1], x[2], x[3], x[4]
    a = ancilla_qubits  # a[0], a[1], a[2], a[3]
    
    # f(x) = 1 iff pattern "?11" matches at any offset in 0..2
    # Offset 0: x[1] AND x[2] (wildcard on x[0])
    # Offset 1: x[2] AND x[3] (wildcard on x[1])
    # Offset 2: x[3] AND x[4] (wildcard on x[2])
    # f(x) = (x[1] AND x[2]) OR (x[2] AND x[3]) OR (x[3] AND x[4])
    
    # COMPUTE PHASE
    # =============
    
    # Compute the three AND terms
    qc.ccx(x[1], x[2], a[0])
    qc.ccx(x[2], x[3], a[1])
    qc.ccx(x[3], x[4], a[2])
    
    # Compute first OR: a[0] OR a[1] -> a[1]
    # Using: a OR b = a XOR b XOR (a AND b)
    qc.ccx(a[0], a[1], a[3])  # a[3] = a[0] AND a[1]
    qc.cx(a[0], a[1])         # a[1] ^= a[0]
    qc.cx(a[3], a[1])         # a[1] ^= a[3] -> a[1] = a[0] OR a[1]
    
    # Uncompute a[0] and a[3] for second OR to use a[3]
    qc.mcx([x[1], x[2], x[3]], a[3])  # Uncompute a[3]
    qc.ccx(x[1], x[2], a[0])          # Uncompute a[0]
    
    # Compute second OR: a[1] OR a[2] -> a[2]
    qc.ccx(a[1], a[2], a[3])  # a[3] = a[1] AND a[2]
    qc.cx(a[1], a[2])         # a[2] ^= a[1]
    qc.cx(a[3], a[2])         # a[2] ^= a[3] -> a[2] = f(x)
    
    # Apply phase flip
    qc.z(a[2])
    
    # UNCOMPUTE PHASE (reverse order)
    # ===============================
    
    # Undo second OR
    qc.cx(a[3], a[2])
    qc.cx(a[1], a[2])
    qc.ccx(a[1], a[2], a[3])
    
    # Restore a[0] and a[3] for undoing first OR
    qc.ccx(x[1], x[2], a[0])
    qc.mcx([x[1], x[2], x[3]], a[3])
    
    # Undo first OR
    qc.cx(a[3], a[1])
    qc.cx(a[0], a[1])
    qc.ccx(a[0], a[1], a[3])
    
    # Uncompute AND terms
    qc.ccx(x[3], x[4], a[2])
    qc.ccx(x[2], x[3], a[1])
    qc.ccx(x[1], x[2], a[0])
