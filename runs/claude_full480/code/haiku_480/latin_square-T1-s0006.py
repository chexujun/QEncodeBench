from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Extract qubit indices for the two free cells at (0,0) and (1,1)
    b0_0 = problem_qubits[0]  # low bit of free cell 0
    b1_0 = problem_qubits[1]  # high bit of free cell 0
    b0_1 = problem_qubits[2]  # low bit of free cell 1
    b1_1 = problem_qubits[3]  # high bit of free cell 1
    
    # For a valid 3x3 Latin square completion, both free cells must have value 1.
    # Value encoding: 00->0, 01->1, 10->2, 11->0 (surjective)
    # Predicate: (b0_0 AND NOT b1_0) AND (b0_1 AND NOT b1_1)
    
    # COMPUTE PHASE: build predicate into ancillas
    # Compute (b0_0 AND NOT b1_0) into ancilla[0]
    qc.x(b1_0)
    qc.ccx(b0_0, b1_0, ancilla_qubits[0])
    qc.x(b1_0)
    
    # Compute (b0_1 AND NOT b1_1) into ancilla[1]
    qc.x(b1_1)
    qc.ccx(b0_1, b1_1, ancilla_qubits[1])
    qc.x(b1_1)
    
    # AND the two conditions into ancilla[2]
    qc.ccx(ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[2])
    
    # PHASE: apply Z to mark valid solutions
    qc.z(ancilla_qubits[2])
    
    # UNCOMPUTE PHASE: restore ancillas to |0>
    qc.ccx(ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[2])
    
    # Uncompute (b0_1 AND NOT b1_1)
    qc.x(b1_1)
    qc.ccx(b0_1, b1_1, ancilla_qubits[1])
    qc.x(b1_1)
    
    # Uncompute (b0_0 AND NOT b1_0)
    qc.x(b1_0)
    qc.ccx(b0_0, b1_0, ancilla_qubits[0])
    qc.x(b1_0)
