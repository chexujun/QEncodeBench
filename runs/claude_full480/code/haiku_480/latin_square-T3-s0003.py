from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Extract problem qubits for the four free cells
    # Each free cell uses 2 qubits: low bit b0, high bit b1
    b00, b01, b10, b11, b20, b21, b30, b31 = problem_qubits
    
    # Use first two ancillas for intermediate XNOR computations
    # Use ancilla_qubits[5] for the final validity result
    a0 = ancilla_qubits[0]
    a1 = ancilla_qubits[1]
    result = ancilla_qubits[5]
    
    # Compute constraint: b00 XNOR b01 (cell 0 must be 00 or 11)
    # XNOR is computed as NOT(b00 XOR b01)
    qc.cx(b00, a0)
    qc.cx(b01, a0)
    qc.x(a0)
    
    # Compute constraint: b30 XNOR b31 (cell 3 must be 00 or 11)
    qc.cx(b30, a1)
    qc.cx(b31, a1)
    qc.x(a1)
    
    # Prepare b11 and b21 for control (need them to be 1 to check they equal 0)
    qc.x(b11)
    qc.x(b21)
    
    # Apply multi-controlled X gate
    # Result = b10 AND b11 AND b20 AND b21 AND a0 AND a1
    # This checks all six constraints:
    # - b10=1 (cell 1 low bit is 1)
    # - b11=0 (cell 1 high bit is 0)
    # - b20=1 (cell 2 low bit is 1)
    # - b21=0 (cell 2 high bit is 0)
    # - a0=1 (cell 0 has equal bits)
    # - a1=1 (cell 3 has equal bits)
    controls = [b10, b11, b20, b21, a0, a1]
    qc.mcx(controls, result)
    
    # Apply phase -1 to valid states
    qc.z(result)
    
    # Uncompute in reverse order
    qc.mcx(controls, result)
    
    # Restore b11 and b21
    qc.x(b11)
    qc.x(b21)
    
    # Uncompute a1
    qc.x(a1)
    qc.cx(b31, a1)
    qc.cx(b30, a1)
    
    # Uncompute a0
    qc.x(a0)
    qc.cx(b01, a0)
    qc.cx(b00, a0)
