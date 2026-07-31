from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Extract problem qubits for the three free cells
    # Free cell 0 at (0,1): problem_qubits[0:2] = (b0_x, b1_x)
    # Free cell 1 at (0,2): problem_qubits[2:4] = (b0_y, b1_y)
    # Free cell 2 at (1,0): problem_qubits[4:6] = (b0_z, b1_z)
    
    b0_x, b1_x = problem_qubits[0], problem_qubits[1]
    b0_y, b1_y = problem_qubits[2], problem_qubits[3]
    b0_z, b1_z = problem_qubits[4], problem_qubits[5]
    
    # Assign ancillas for computation
    a_main = ancilla_qubits[0]  # Main ancilla for final result
    a_p2 = ancilla_qubits[1]    # b0_y AND (NOT b1_y)
    a_p3 = ancilla_qubits[2]    # b0_z AND (NOT b1_z)
    a_xor = ancilla_qubits[3]   # XNOR(b0_x, b1_x)
    a_temp = ancilla_qubits[4]  # Intermediate AND result
    
    # The unique valid Latin square completion requires:
    # Free cell 0 = 0 (encoded 00 or 11): XNOR(b0_x, b1_x) = 1
    # Free cell 1 = 1 (encoded 01): b0_y=1, b1_y=0
    # Free cell 2 = 1 (encoded 01): b0_z=1, b1_z=0
    
    # Compute p2 = b0_y AND (NOT b1_y)
    qc.x(b1_y)
    qc.ccx(b0_y, b1_y, a_p2)
    qc.x(b1_y)
    
    # Compute p3 = b0_z AND (NOT b1_z)
    qc.x(b1_z)
    qc.ccx(b0_z, b1_z, a_p3)
    qc.x(b1_z)
    
    # Compute p1 = XNOR(b0_x, b1_x) via XOR then negate
    qc.cx(b0_x, a_xor)
    qc.cx(b1_x, a_xor)
    qc.x(a_xor)  # a_xor now = XNOR(b0_x, b1_x)
    
    # Combine predicates: a_main = p1 AND p2 AND p3
    qc.ccx(a_xor, a_p2, a_temp)  # a_temp = p1 AND p2
    qc.ccx(a_temp, a_p3, a_main)  # a_main = (p1 AND p2) AND p3
    
    # Apply phase -1 if a_main is set
    qc.z(a_main)
    
    # Uncompute in reverse order
    qc.ccx(a_temp, a_p3, a_main)
    qc.ccx(a_xor, a_p2, a_temp)
    qc.x(a_xor)
    qc.cx(b1_x, a_xor)
    qc.cx(b0_x, a_xor)
    qc.x(b1_z)
    qc.ccx(b0_z, b1_z, a_p3)
    qc.x(b1_z)
    qc.x(b1_y)
    qc.ccx(b0_y, b1_y, a_p2)
    qc.x(b1_y)
