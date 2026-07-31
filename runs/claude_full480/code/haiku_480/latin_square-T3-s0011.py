from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    """
    Oracle for 3x3 Latin square completion.
    
    Marks the unique valid completion [0, 2, 2, 0] where:
    - Cell 0 at (1,0) must be 0
    - Cell 1 at (1,2) must be 2
    - Cell 2 at (2,1) must be 2
    - Cell 3 at (2,2) must be 0
    
    Each cell uses 2 problem qubits encoding value via: code = b0 + 2*b1.
    """
    # Extract problem qubits (2 per cell)
    b0_0, b1_0 = problem_qubits[0], problem_qubits[1]
    b0_1, b1_1 = problem_qubits[2], problem_qubits[3]
    b0_2, b1_2 = problem_qubits[4], problem_qubits[5]
    b0_3, b1_3 = problem_qubits[6], problem_qubits[7]
    
    # Use ancillas: 4 for condition checks, 1 for AND result
    a0, a1, a2, a3, temp1 = ancilla_qubits[0:5]
    
    # === COMPUTE PHASE ===
    
    # Check cell[0] = 0: requires code 00 or 11, i.e., b0_0 == b1_0
    # Compute NOT(b0_0 XOR b1_0)
    qc.cx(b0_0, a0)
    qc.cx(b1_0, a0)
    qc.x(a0)
    
    # Check cell[1] = 2: requires code 10, i.e., b1_1 = 1 AND b0_1 = 0
    qc.x(b0_1)  # flip b0_1 to check NOT(b0_1)
    qc.ccx(b1_1, b0_1, a1)
    qc.x(b0_1)  # restore b0_1
    
    # Check cell[2] = 2: requires code 10, i.e., b1_2 = 1 AND b0_2 = 0
    qc.x(b0_2)
    qc.ccx(b1_2, b0_2, a2)
    qc.x(b0_2)
    
    # Check cell[3] = 0: requires code 00 or 11, i.e., b0_3 == b1_3
    # Compute NOT(b0_3 XOR b1_3)
    qc.cx(b0_3, a3)
    qc.cx(b1_3, a3)
    qc.x(a3)
    
    # AND all four checks: set temp1 = 1 iff all conditions hold
    qc.mcx([a0, a1, a2, a3], temp1)
    
    # Apply phase: -1 on marked states
    qc.z(temp1)
    
    # === UNCOMPUTE PHASE ===
    
    # Uncompute AND
    qc.mcx([a0, a1, a2, a3], temp1)
    
    # Uncompute cell[3] check
    qc.x(a3)
    qc.cx(b1_3, a3)
    qc.cx(b0_3, a3)
    
    # Uncompute cell[2] check
    qc.x(b0_2)
    qc.ccx(b1_2, b0_2, a2)
    qc.x(b0_2)
    
    # Uncompute cell[1] check
    qc.x(b0_1)
    qc.ccx(b1_1, b0_1, a1)
    qc.x(b0_1)
    
    # Uncompute cell[0] check
    qc.x(a0)
    qc.cx(b1_0, a0)
    qc.cx(b0_0, a0)
