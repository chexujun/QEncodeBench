from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # 3x3 Latin square completion problem
    # Free cells: (0,0)→f0, (0,2)→f1, (2,2)→f2
    # Valid solution: f0=2, f1=0, f2=1
    #
    # Decoding: c = b0 + 2*b1 where c∈{0,1,2,3}
    # 00→0, 01→1, 10→2, 11→0
    #
    # Constraints: f0 must be 2, f1 must be 0, f2 must be 1
    
    # Extract problem qubits
    b0_0, b1_0 = problem_qubits[0], problem_qubits[1]  # f0
    b0_1, b1_1 = problem_qubits[2], problem_qubits[3]  # f1
    b0_2, b1_2 = problem_qubits[4], problem_qubits[5]  # f2
    
    # Ancilla qubits for intermediate results
    c0 = ancilla_qubits[0]      # (NOT b0_0) AND b1_0: true iff f0=2
    c1 = ancilla_qubits[1]      # (NOT b0_1) AND (NOT b1_1): true iff f1=0
    c2 = ancilla_qubits[2]      # b0_2 AND (NOT b1_2): true iff f2=1
    c01 = ancilla_qubits[3]     # c0 AND c1
    valid = ancilla_qubits[4]   # c0 AND c1 AND c2
    
    # COMPUTE PHASE
    
    # Compute c0 = (NOT b0_0) AND b1_0
    qc.x(b0_0)
    qc.ccx(b0_0, b1_0, c0)
    qc.x(b0_0)
    
    # Compute c1 = (NOT b0_1) AND (NOT b1_1)
    qc.x(b0_1)
    qc.x(b1_1)
    qc.ccx(b0_1, b1_1, c1)
    qc.x(b1_1)
    qc.x(b0_1)
    
    # Compute c2 = b0_2 AND (NOT b1_2)
    qc.x(b1_2)
    qc.ccx(b0_2, b1_2, c2)
    qc.x(b1_2)
    
    # Compute c01 = c0 AND c1
    qc.ccx(c0, c1, c01)
    
    # Compute valid = c01 AND c2
    qc.ccx(c01, c2, valid)
    
    # Apply phase -1 to valid state
    qc.z(valid)
    
    # UNCOMPUTE (reverse order)
    
    # Uncompute valid
    qc.ccx(c01, c2, valid)
    
    # Uncompute c01
    qc.ccx(c0, c1, c01)
    
    # Uncompute c2
    qc.x(b1_2)
    qc.ccx(b0_2, b1_2, c2)
    qc.x(b1_2)
    
    # Uncompute c1
    qc.x(b0_1)
    qc.x(b1_1)
    qc.ccx(b0_1, b1_1, c1)
    qc.x(b1_1)
    qc.x(b0_1)
    
    # Uncompute c0
    qc.x(b0_0)
    qc.ccx(b0_0, b1_0, c0)
    qc.x(b0_0)
