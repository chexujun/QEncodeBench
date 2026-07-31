from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Extract problem qubits for the 4 free cells (2 bits each)
    # Free cells: (0,0), (1,0), (2,0), (2,1)
    b0_0, b1_0 = problem_qubits[0], problem_qubits[1]  # Cell 0
    b0_1, b1_1 = problem_qubits[2], problem_qubits[3]  # Cell 1
    b0_2, b1_2 = problem_qubits[4], problem_qubits[5]  # Cell 2
    b0_3, b1_3 = problem_qubits[6], problem_qubits[7]  # Cell 3
    
    # Ancillas for constraints and intermediate AND computations
    a0, a1, a2, a3, a4, a5 = ancilla_qubits
    
    # === COMPUTE CONSTRAINTS ===
    
    # Constraint 1: a0 = NOT(b0_0 XOR b1_0) [cell 0 must have value 0, so code ∈ {0,3}]
    qc.cx(b0_0, a0)
    qc.cx(b1_0, a0)
    qc.x(a0)
    
    # Constraint 2: a1 = b0_1 AND NOT b1_1 [cell 1 must have value 1, so code = 1]
    qc.x(b1_1)
    qc.ccx(b0_1, b1_1, a1)
    qc.x(b1_1)
    
    # Constraint 3: a2 = NOT b0_2 AND b1_2 [cell 2 must have value 2, so code = 2]
    qc.x(b0_2)
    qc.ccx(b0_2, b1_2, a2)
    qc.x(b0_2)
    
    # Constraint 4: a3 = NOT(b0_3 XOR b1_3) [cell 3 must have value 0, so code ∈ {0,3}]
    qc.cx(b0_3, a3)
    qc.cx(b1_3, a3)
    qc.x(a3)
    
    # === COMPUTE AND OF ALL CONSTRAINTS ===
    
    # a4 = a0 AND a1
    qc.ccx(a0, a1, a4)
    
    # a5 = a4 AND a2 = (a0 AND a1 AND a2)
    qc.ccx(a4, a2, a5)
    
    # Clear a4 for reuse
    qc.ccx(a0, a1, a4)
    
    # a4 = a5 AND a3 = (a0 AND a1 AND a2 AND a3)
    qc.ccx(a5, a3, a4)
    
    # === APPLY PHASE ===
    qc.z(a4)
    
    # === UNCOMPUTE (REVERSE ORDER) ===
    
    # Undo a4 = a5 AND a3
    qc.ccx(a5, a3, a4)
    
    # Undo clear of a4
    qc.ccx(a0, a1, a4)
    
    # Undo a5 = a4 AND a2
    qc.ccx(a4, a2, a5)
    
    # Undo a4 = a0 AND a1
    qc.ccx(a0, a1, a4)
    
    # === UNCOMPUTE CONSTRAINTS ===
    
    # Undo constraint 4
    qc.x(a3)
    qc.cx(b1_3, a3)
    qc.cx(b0_3, a3)
    
    # Undo constraint 3
    qc.x(b0_2)
    qc.ccx(b0_2, b1_2, a2)
    qc.x(b0_2)
    
    # Undo constraint 2
    qc.x(b1_1)
    qc.ccx(b0_1, b1_1, a1)
    qc.x(b1_1)
    
    # Undo constraint 1
    qc.x(a0)
    qc.cx(b1_0, a0)
    qc.cx(b0_0, a0)
