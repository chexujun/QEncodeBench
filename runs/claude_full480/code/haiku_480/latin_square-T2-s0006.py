from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    # problem_qubits = [b0_0, b1_0, b0_1, b1_1, b0_2, b1_2]
    # Free cell 0 (row 0, col 0): c0 = b0_0 + 2*b1_0, must be 1
    # Free cell 1 (row 2, col 1): c1 = b0_1 + 2*b1_1, must be 1
    # Free cell 2 (row 2, col 2): c2 = b0_2 + 2*b1_2, must be 2
    
    # Constraints:
    # c0 = 1: b0_0 = 1 AND b1_0 = 0
    # c1 = 1: b0_1 = 1 AND b1_1 = 0
    # c2 = 2: b0_2 = 0 AND b1_2 = 1
    
    b0_0, b1_0, b0_1, b1_1, b0_2, b1_2 = problem_qubits[:6]
    
    # Ancillas for intermediate computations
    a0, a1, a2, a_final, temp = ancilla_qubits[:5]
    
    # Compute condition for c0 = 1: b0_0 AND NOT b1_0
    qc.x(b1_0)
    qc.ccx(b0_0, b1_0, a0)
    qc.x(b1_0)
    
    # Compute condition for c1 = 1: b0_1 AND NOT b1_1
    qc.x(b1_1)
    qc.ccx(b0_1, b1_1, a1)
    qc.x(b1_1)
    
    # Compute condition for c2 = 2: NOT b0_2 AND b1_2
    qc.x(b0_2)
    qc.ccx(b0_2, b1_2, a2)
    qc.x(b0_2)
    
    # Combine all conditions: a_final = a0 AND a1 AND a2
    qc.ccx(a0, a1, temp)
    qc.ccx(temp, a2, a_final)
    
    # Apply Z gate to apply phase
    qc.z(a_final)
    
    # Uncompute in reverse order
    qc.ccx(temp, a2, a_final)
    qc.ccx(a0, a1, temp)
    
    # Uncompute a2
    qc.x(b0_2)
    qc.ccx(b0_2, b1_2, a2)
    qc.x(b0_2)
    
    # Uncompute a1
    qc.x(b1_1)
    qc.ccx(b0_1, b1_1, a1)
    qc.x(b1_1)
    
    # Uncompute a0
    qc.x(b1_0)
    qc.ccx(b0_0, b1_0, a0)
    qc.x(b1_0)
