from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    """
    Grover oracle for pattern matching.
    Pattern: "0110" (positions 0, 1, 2, 3)
    Text: 8 bits on problem_qubits[0:8]
    Offsets where pattern must be checked: 0, 1, 2, 3, 4
    """
    pattern = [0, 1, 1, 0]
    offsets = [0, 1, 2, 3, 4]
    
    # Compute match[o] into ancilla[o] for each offset o
    # match[o] = 1 iff pattern matches starting at offset o
    for offset_idx, offset in enumerate(offsets):
        anc = ancilla_qubits[offset_idx]
        
        # Flip qubits where pattern requires a 0 (so they become control qubits for the 1-states)
        for j in range(4):
            if pattern[j] == 0:
                qc.x(problem_qubits[offset + j])
        
        # Apply MCX: ancilla becomes 1 iff all pattern qubits are 1
        controls = [problem_qubits[offset + j] for j in range(4)]
        qc.mcx(controls, anc)
        
        # Restore flipped qubits
        for j in range(4):
            if pattern[j] == 0:
                qc.x(problem_qubits[offset + j])
    
    # Compute: result = NOT(match[0] OR match[1] OR match[2] OR match[3] OR match[4])
    # Using De Morgan: OR = NOT(AND of NOTs)
    
    # Flip ancilla[0:5] to get their NOTs
    for i in range(5):
        qc.x(ancilla_qubits[i])
    
    # Apply MCX: ancilla[5] = AND of (NOT match[0..4])
    controls = ancilla_qubits[0:5]
    target = ancilla_qubits[5]
    qc.mcx(controls, target)
    
    # Restore ancilla[0:5]
    for i in range(5):
        qc.x(ancilla_qubits[i])
    
    # Flip ancilla[5] to get the OR result
    qc.x(ancilla_qubits[5])
    
    # Apply Z gate to mark solutions with phase -1
    qc.z(ancilla_qubits[5])
    
    # Uncompute: reverse all operations
    qc.x(ancilla_qubits[5])
    
    for i in range(5):
        qc.x(ancilla_qubits[i])
    
    qc.mcx(controls, target)
    
    for i in range(5):
        qc.x(ancilla_qubits[i])
    
    # Uncompute each match computation (reverse order)
    for offset_idx in range(4, -1, -1):
        offset = offsets[offset_idx]
        anc = ancilla_qubits[offset_idx]
        
        for j in range(4):
            if pattern[j] == 0:
                qc.x(problem_qubits[offset + j])
        
        controls = [problem_qubits[offset + j] for j in range(4)]
        qc.mcx(controls, anc)
        
        for j in range(4):
            if pattern[j] == 0:
                qc.x(problem_qubits[offset + j])
