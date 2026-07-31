from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    """
    Oracle for 3x3 Latin square completion.
    Marks the unique solution: free_cell[0]=1, free_cell[1]=2, free_cell[2]=0
    """
    # Unpack problem qubits for each free cell (LSB first)
    b0_0, b0_1 = problem_qubits[0], problem_qubits[1]
    b1_0, b1_1 = problem_qubits[2], problem_qubits[3]
    b2_0, b2_1 = problem_qubits[4], problem_qubits[5]
    
    # Ancilla qubits
    c0 = ancilla_qubits[0]      # Constraint: cell[0] == 1
    c1 = ancilla_qubits[1]      # Constraint: cell[1] == 2
    c2 = ancilla_qubits[2]      # Constraint: cell[2] == 0
    tmp = ancilla_qubits[3]     # Temporary for AND operations
    result = ancilla_qubits[4]  # Final phase qubit
    
    # COMPUTE: Evaluate all constraints
    
    # c0 = 1 iff cell[0] has value 1 (code 01: b0_0=1, b0_1=0)
    qc.x(b0_1)
    qc.ccx(b0_0, b0_1, c0)
    qc.x(b0_1)
    
    # c1 = 1 iff cell[1] has value 2 (code 10: b1_0=0, b1_1=1)
    qc.x(b1_0)
    qc.ccx(b1_0, b1_1, c1)
    qc.x(b1_0)
    
    # c2 = 1 iff cell[2] has value 0 (code 00 or 11: b2_0 == b2_1)
    qc.cx(b2_0, c2)
    qc.cx(b2_1, c2)
    qc.x(c2)
    
    # result = c0 AND c1 AND c2
    qc.ccx(c0, c1, tmp)
    qc.ccx(tmp, c2, result)
    
    # APPLY PHASE: -1 if result == 1
    qc.z(result)
    
    # UNCOMPUTE: Reverse all operations
    
    qc.ccx(tmp, c2, result)
    qc.ccx(c0, c1, tmp)
    
    qc.x(c2)
    qc.cx(b2_1, c2)
    qc.cx(b2_0, c2)
    
    qc.x(b1_0)
    qc.ccx(b1_0, b1_1, c1)
    qc.x(b1_0)
    
    qc.x(b0_1)
    qc.ccx(b0_0, b0_1, c0)
    qc.x(b0_1)
