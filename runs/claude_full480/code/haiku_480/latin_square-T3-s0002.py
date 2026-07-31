from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Extract qubit indices
    # Free cell 0 (row 0, col 2): problem_qubits[0,1]
    # Free cell 1 (row 1, col 2): problem_qubits[2,3]
    # Free cell 2 (row 2, col 1): problem_qubits[4,5]
    # Free cell 3 (row 2, col 2): problem_qubits[6,7]
    c0_low, c0_high = problem_qubits[0], problem_qubits[1]
    c1_low, c1_high = problem_qubits[2], problem_qubits[3]
    c2_low, c2_high = problem_qubits[4], problem_qubits[5]
    c3_low, c3_high = problem_qubits[6], problem_qubits[7]
    
    flag, a0, a1, a2, a3, a4 = ancilla_qubits
    
    # Constraint 0: cell (0,2) must be 2, so c0_low=0, c0_high=1
    # a0 = (NOT c0_low) AND c0_high
    qc.x(c0_low)
    qc.ccx(c0_low, c0_high, a0)
    qc.x(c0_low)
    
    # Constraint 1: cell (1,2) must be 0, so c1 in {0,3}
    # This requires c1_low == c1_high (both 0 or both 1)
    # a1 = NOT (c1_low XOR c1_high)
    qc.cx(c1_low, a1)
    qc.cx(c1_high, a1)
    qc.x(a1)
    
    # Constraint 2: cell (2,1) must be 0, so c2 in {0,3}
    # a2 = NOT (c2_low XOR c2_high)
    qc.cx(c2_low, a2)
    qc.cx(c2_high, a2)
    qc.x(a2)
    
    # Constraint 3: cell (2,2) must be 1, so c3_low=1, c3_high=0
    # a3 = c3_low AND (NOT c3_high)
    qc.x(c3_high)
    qc.ccx(c3_low, c3_high, a3)
    qc.x(c3_high)
    
    # Compute flag = a0 AND a1 AND a2 using a4 as scratch
    qc.ccx(a0, a1, a4)
    qc.ccx(a4, a2, flag)
    
    # Apply phase when flag AND a3 (i.e., all constraints satisfied)
    qc.cz(flag, a3)
    
    # Uncompute flag
    qc.ccx(a4, a2, flag)
    qc.ccx(a0, a1, a4)
    
    # Uncompute constraint 3
    qc.x(c3_high)
    qc.ccx(c3_low, c3_high, a3)
    qc.x(c3_high)
    
    # Uncompute constraint 2
    qc.x(a2)
    qc.cx(c2_high, a2)
    qc.cx(c2_low, a2)
    
    # Uncompute constraint 1
    qc.x(a1)
    qc.cx(c1_high, a1)
    qc.cx(c1_low, a1)
    
    # Uncompute constraint 0
    qc.x(c0_low)
    qc.ccx(c0_low, c0_high, a0)
    qc.x(c0_low)
