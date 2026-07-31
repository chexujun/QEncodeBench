from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    b0_0, b1_0 = problem_qubits[0], problem_qubits[1]
    b0_1, b1_1 = problem_qubits[2], problem_qubits[3]
    b0_2, b1_2 = problem_qubits[4], problem_qubits[5]
    b0_3, b1_3 = problem_qubits[6], problem_qubits[7]
    
    a0, a1, a2, a3, a4, a5 = ancilla_qubits
    
    # Compute constraint 1: cell0 = 2 (binary 10)
    # c1 = NOT(b0_0) AND b1_0 → a0
    qc.x(b0_0)
    qc.ccx(b0_0, b1_0, a0)
    qc.x(b0_0)
    
    # Compute constraint 2: cell1 = 0 (binary 00 or 11)
    # c2 = NOT(b0_1 XOR b1_1) → a1
    qc.cx(b0_1, a1)
    qc.cx(b1_1, a1)
    qc.x(a1)
    
    # Compute constraint 3: cell2 = 1 (binary 01)
    # c3 = b0_2 AND NOT(b1_2) → a2
    qc.x(b1_2)
    qc.ccx(b0_2, b1_2, a2)
    qc.x(b1_2)
    
    # Compute constraint 4: cell3 = 0 (binary 00 or 11)
    # c4 = NOT(b0_3 XOR b1_3) → a3
    qc.cx(b0_3, a3)
    qc.cx(b1_3, a3)
    qc.x(a3)
    
    # Compute AND of all constraints: a4 = a0 AND a1 AND a2 AND a3
    qc.ccx(a0, a1, a4)
    qc.ccx(a4, a2, a5)
    qc.ccx(a0, a1, a4)
    qc.ccx(a5, a3, a4)
    
    # Apply phase: Z gate applies -1 phase when a4 = |1⟩
    qc.z(a4)
    
    # Uncompute AND in reverse
    qc.ccx(a5, a3, a4)
    qc.ccx(a0, a1, a4)
    qc.ccx(a4, a2, a5)
    qc.ccx(a0, a1, a4)
    
    # Uncompute constraint 4
    qc.x(a3)
    qc.cx(b1_3, a3)
    qc.cx(b0_3, a3)
    
    # Uncompute constraint 3
    qc.x(b1_2)
    qc.ccx(b0_2, b1_2, a2)
    qc.x(b1_2)
    
    # Uncompute constraint 2
    qc.x(a1)
    qc.cx(b1_1, a1)
    qc.cx(b0_1, a1)
    
    # Uncompute constraint 1
    qc.x(b0_0)
    qc.ccx(b0_0, b1_0, a0)
    qc.x(b0_0)
