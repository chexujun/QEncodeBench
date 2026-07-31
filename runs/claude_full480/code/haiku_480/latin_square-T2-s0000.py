from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    # Extract bits for each free cell
    b0_0, b1_0 = problem_qubits[0], problem_qubits[1]  # free cell 0
    b0_1, b1_1 = problem_qubits[2], problem_qubits[3]  # free cell 1
    b0_2, b1_2 = problem_qubits[4], problem_qubits[5]  # free cell 2
    
    # Ancillas for constraint results
    a0 = ancilla_qubits[0]  # constraint: v0 = 0 <=> NOT(b0_0 XOR b1_0)
    a1 = ancilla_qubits[1]  # constraint: v1 = 2 <=> (NOT b0_1) AND b1_1
    a2 = ancilla_qubits[2]  # constraint: v2 = 0 <=> NOT(b0_2 XOR b1_2)
    
    # Ancillas for intermediate computations
    temp_not_b0_1 = ancilla_qubits[3]
    temp_and_01 = ancilla_qubits[4]
    a_final = ancilla_qubits[5]
    
    # ========== COMPUTE PHASE ==========
    
    # Compute a0 = NOT(b0_0 XOR b1_0)
    qc.x(a0)
    qc.cx(b0_0, a0)
    qc.cx(b1_0, a0)
    
    # Compute a1 = (NOT b0_1) AND b1_1
    qc.x(temp_not_b0_1)
    qc.cx(b0_1, temp_not_b0_1)
    qc.ccx(temp_not_b0_1, b1_1, a1)
    
    # Compute a2 = NOT(b0_2 XOR b1_2)
    qc.x(a2)
    qc.cx(b0_2, a2)
    qc.cx(b1_2, a2)
    
    # Combine: a_final = a0 AND a1 AND a2
    qc.ccx(a0, a1, temp_and_01)
    qc.ccx(temp_and_01, a2, a_final)
    
    # ========== APPLY PHASE ==========
    qc.z(a_final)
    
    # ========== UNCOMPUTE PHASE ==========
    
    # Uncompute final AND
    qc.ccx(temp_and_01, a2, a_final)
    qc.ccx(a0, a1, temp_and_01)
    
    # Uncompute a2
    qc.cx(b1_2, a2)
    qc.cx(b0_2, a2)
    qc.x(a2)
    
    # Uncompute a1
    qc.ccx(temp_not_b0_1, b1_1, a1)
    qc.cx(b0_1, temp_not_b0_1)
    qc.x(temp_not_b0_1)
    
    # Uncompute a0
    qc.cx(b1_0, a0)
    qc.cx(b0_0, a0)
    qc.x(a0)
