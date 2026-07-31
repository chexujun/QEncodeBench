from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Extract problem qubits for the two free cells
    b0_0, b1_0 = problem_qubits[0], problem_qubits[1]
    b0_1, b1_1 = problem_qubits[2], problem_qubits[3]
    
    # Use first 3 ancilla qubits
    a0 = ancilla_qubits[0]
    a1 = ancilla_qubits[1]
    a2 = ancilla_qubits[2]
    
    # Compute: a0 = b0_0 XNOR b1_0
    # Free cell 0 at (0,2) decodes to 0 iff code is 00 or 11
    # i.e., iff b0_0 = b1_0, equivalently NOT(b0_0 XOR b1_0)
    qc.cx(b0_0, a0)
    qc.cx(b1_0, a0)
    qc.x(a0)
    
    # Compute: a1 = b0_1 XNOR b1_1
    # Free cell 1 at (2,1) decodes to 0 iff code is 00 or 11
    qc.cx(b0_1, a1)
    qc.cx(b1_1, a1)
    qc.x(a1)
    
    # Compute: a2 = a0 AND a1
    # Latin square is valid iff both cells decode to 0
    qc.ccx(a0, a1, a2)
    
    # Apply phase
    qc.z(a2)
    
    # Uncompute to return ancillas to |0>
    qc.ccx(a0, a1, a2)
    qc.x(a1)
    qc.cx(b1_1, a1)
    qc.cx(b0_1, a1)
    qc.x(a0)
    qc.cx(b1_0, a0)
    qc.cx(b0_0, a0)
