from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    b0_0, b1_0 = problem_qubits[0], problem_qubits[1]
    b0_1, b1_1 = problem_qubits[2], problem_qubits[3]
    b0_2, b1_2 = problem_qubits[4], problem_qubits[5]
    
    anc = ancilla_qubits
    
    # Compute NOT b0_0 into anc[0]
    qc.x(anc[0])
    qc.cx(b0_0, anc[0])
    
    # Compute NOT b1_0 into anc[1]
    qc.x(anc[1])
    qc.cx(b1_0, anc[1])
    
    # Compute (NOT b0_0) AND (NOT b1_0) into anc[2]
    qc.ccx(anc[0], anc[1], anc[2])
    
    # Compute b0_0 AND b1_0 into anc[3]
    qc.ccx(b0_0, b1_0, anc[3])
    
    # Compute (b0_0 == b1_0) into anc[4]
    # = (NOT b0_0 AND NOT b1_0) OR (b0_0 AND b1_0)
    qc.cx(anc[2], anc[4])
    qc.cx(anc[3], anc[4])
    
    # Compute NOT b0_1 into anc[5]
    qc.x(anc[5])
    qc.cx(b0_1, anc[5])
    
    # Compute NOT b0_2 into anc[6]
    qc.x(anc[6])
    qc.cx(b0_2, anc[6])
    
    # Compute cascading AND of all conditions
    qc.ccx(anc[4], anc[5], anc[7])
    qc.ccx(anc[7], b1_1, anc[8])
    qc.ccx(anc[8], anc[6], anc[9])
    qc.ccx(anc[9], b1_2, anc[10])
    
    # Apply phase
    qc.z(anc[10])
    
    # Uncompute (reverse order)
    qc.ccx(anc[9], b1_2, anc[10])
    qc.ccx(anc[8], anc[6], anc[9])
    qc.ccx(anc[7], b1_1, anc[8])
    qc.ccx(anc[4], anc[5], anc[7])
    
    qc.cx(b0_2, anc[6])
    qc.x(anc[6])
    
    qc.cx(b0_1, anc[5])
    qc.x(anc[5])
    
    qc.cx(anc[3], anc[4])
    qc.cx(anc[2], anc[4])
    qc.ccx(b0_0, b1_0, anc[3])
    qc.ccx(anc[0], anc[1], anc[2])
    
    qc.cx(b1_0, anc[1])
    qc.x(anc[1])
    
    qc.cx(b0_0, anc[0])
    qc.x(anc[0])
