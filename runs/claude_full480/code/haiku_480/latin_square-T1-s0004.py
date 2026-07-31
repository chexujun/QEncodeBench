from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Problem qubits for two free cells: (1,2) and (2,0)
    b0_0, b1_0, b0_1, b1_1 = problem_qubits[:4]
    
    # Ancillas for XOR and AND operations
    a0 = ancilla_qubits[0]
    a1 = ancilla_qubits[1]
    and_result = ancilla_qubits[2]
    
    # Compute a0 = b0_0 XOR b1_0 (0 iff free cell 0 has value 0)
    qc.cx(b0_0, a0)
    qc.cx(b1_0, a0)
    
    # Compute a1 = b0_1 XOR b1_1 (0 iff free cell 1 has value 0)
    qc.cx(b0_1, a1)
    qc.cx(b1_1, a1)
    
    # Flip to get NOT values (1 iff value is 0)
    qc.x(a0)
    qc.x(a1)
    
    # Compute AND: mark when both values are 0
    qc.ccx(a0, a1, and_result)
    
    # Apply phase
    qc.z(and_result)
    
    # Uncompute AND
    qc.ccx(a0, a1, and_result)
    
    # Unflip
    qc.x(a1)
    qc.x(a0)
    
    # Uncompute a1
    qc.cx(b0_1, a1)
    qc.cx(b1_1, a1)
    
    # Uncompute a0
    qc.cx(b0_0, a0)
    qc.cx(b1_0, a0)
