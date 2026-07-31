from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    b0_0, b1_0 = problem_qubits[0], problem_qubits[1]
    b0_1, b1_1 = problem_qubits[2], problem_qubits[3]
    b0_2, b1_2 = problem_qubits[4], problem_qubits[5]
    
    # Ancillas
    c1 = ancilla_qubits[0]
    c2 = ancilla_qubits[1]
    c3 = ancilla_qubits[2]
    tmp1 = ancilla_qubits[3]
    tmp2 = ancilla_qubits[4]
    result = ancilla_qubits[5]
    
    # === COMPUTE ===
    
    # Constraint 1: cell[0,1] = 1 requires b0[0]=1 AND b1[0]=0
    qc.cx(b1_0, tmp1)
    qc.x(tmp1)
    qc.ccx(b0_0, tmp1, c1)
    
    # Constraint 2: cell[1,1] = 0 requires code in {00,11}, i.e., b0[1] XNOR b1[1]
    qc.cx(b0_1, c2)
    qc.cx(b1_1, c2)
    qc.x(c2)
    
    # Constraint 3: cell[2,0] = 0 requires code in {00,11}, i.e., b0[2] XNOR b1[2]
    qc.cx(b0_2, c3)
    qc.cx(b1_2, c3)
    qc.x(c3)
    
    # Combine all constraints: result = c1 AND c2 AND c3
    qc.ccx(c1, c2, tmp2)
    qc.ccx(tmp2, c3, result)
    
    # === PHASE ===
    qc.z(result)
    
    # === UNCOMPUTE ===
    
    qc.ccx(tmp2, c3, result)
    qc.ccx(c1, c2, tmp2)
    
    # Uncompute constraint 3
    qc.x(c3)
    qc.cx(b1_2, c3)
    qc.cx(b0_2, c3)
    
    # Uncompute constraint 2
    qc.x(c2)
    qc.cx(b1_1, c2)
    qc.cx(b0_1, c2)
    
    # Uncompute constraint 1
    qc.ccx(b0_0, tmp1, c1)
    qc.x(tmp1)
    qc.cx(b1_0, tmp1)
