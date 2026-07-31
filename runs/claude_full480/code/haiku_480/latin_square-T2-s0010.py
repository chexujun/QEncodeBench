from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    b0_0, b1_0, b0_1, b1_1, b0_2, b1_2 = problem_qubits[:6]
    anc = ancilla_qubits
    
    # Check constraint 1: free[0] = 1, i.e., (b0_0, b1_0) = (1, 0)
    # Compute: anc[0] = b0_0 AND NOT b1_0
    qc.x(b1_0)
    qc.ccx(b0_0, b1_0, anc[0])
    qc.x(b1_0)
    
    # Check constraint 2: free[1] = 2, i.e., (b0_1, b1_1) = (0, 1)
    # Compute: anc[1] = NOT b0_1 AND b1_1
    qc.x(b0_1)
    qc.ccx(b0_1, b1_1, anc[1])
    qc.x(b0_1)
    
    # Check constraint 3: free[2] = 1, i.e., (b0_2, b1_2) = (1, 0)
    # Compute: anc[2] = b0_2 AND NOT b1_2
    qc.x(b1_2)
    qc.ccx(b0_2, b1_2, anc[2])
    qc.x(b1_2)
    
    # Compute overall validity: anc[4] = anc[0] AND anc[1] AND anc[2]
    qc.ccx(anc[0], anc[1], anc[3])
    qc.ccx(anc[3], anc[2], anc[4])
    
    # Apply phase to valid states
    qc.z(anc[4])
    
    # Uncompute (mirror the compute phase)
    qc.ccx(anc[3], anc[2], anc[4])
    qc.ccx(anc[0], anc[1], anc[3])
    
    qc.x(b1_2)
    qc.ccx(b0_2, b1_2, anc[2])
    qc.x(b1_2)
    
    qc.x(b0_1)
    qc.ccx(b0_1, b1_1, anc[1])
    qc.x(b0_1)
    
    qc.x(b1_0)
    qc.ccx(b0_0, b1_0, anc[0])
    qc.x(b1_0)
