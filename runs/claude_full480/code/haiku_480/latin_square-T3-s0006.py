from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    
    b = problem_qubits
    a = ancilla_qubits
    
    # === COMPUTE CONSTRAINTS ===
    
    # Constraint 0: cell 0 (b[0], b[1]) must decode to value 0 (codes 00 or 11)
    # Check: b[0] XNOR b[1], result into a[0]
    qc.cx(b[0], a[4])
    qc.cx(b[1], a[4])
    qc.x(a[4])
    qc.cx(a[4], a[0])
    qc.x(a[4])
    qc.cx(b[1], a[4])
    qc.cx(b[0], a[4])
    
    # Constraint 1: cell 1 (b[2], b[3]) must decode to value 0
    # Check: b[2] XNOR b[3], result into a[1]
    qc.cx(b[2], a[4])
    qc.cx(b[3], a[4])
    qc.x(a[4])
    qc.cx(a[4], a[1])
    qc.x(a[4])
    qc.cx(b[3], a[4])
    qc.cx(b[2], a[4])
    
    # Constraint 2: cell 2 (b[4], b[5]) must decode to value 2 (code 10)
    # Check: NOT b[4] AND b[5], result into a[2]
    qc.x(b[4])
    qc.ccx(b[4], b[5], a[2])
    qc.x(b[4])
    
    # Constraint 3: cell 3 (b[6], b[7]) must decode to value 1 (code 01)
    # Check: b[6] AND NOT b[7], result into a[3]
    qc.x(b[7])
    qc.ccx(b[6], b[7], a[3])
    qc.x(b[7])
    
    # === APPLY PHASE ===
    
    # Apply phase -1 if all constraints are satisfied
    qc.mcx([a[0], a[1], a[2], a[3]], a[4])
    qc.z(a[4])
    qc.mcx([a[0], a[1], a[2], a[3]], a[4])
    
    # === UNCOMPUTE CONSTRAINTS (reverse order) ===
    
    # Uncompute constraint 3
    qc.x(b[7])
    qc.ccx(b[6], b[7], a[3])
    qc.x(b[7])
    
    # Uncompute constraint 2
    qc.x(b[4])
    qc.ccx(b[4], b[5], a[2])
    qc.x(b[4])
    
    # Uncompute constraint 1
    qc.cx(b[2], a[4])
    qc.cx(b[3], a[4])
    qc.x(a[4])
    qc.cx(a[4], a[1])
    qc.x(a[4])
    qc.cx(b[3], a[4])
    qc.cx(b[2], a[4])
    
    # Uncompute constraint 0
    qc.cx(b[0], a[4])
    qc.cx(b[1], a[4])
    qc.x(a[4])
    qc.cx(a[4], a[0])
    qc.x(a[4])
    qc.cx(b[1], a[4])
    qc.cx(b[0], a[4])
