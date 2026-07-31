from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    """
    Oracle for substring pattern matching in Grover's algorithm.
    Marks states where the pattern "0101" appears as a contiguous substring.
    """
    pattern = [0, 1, 0, 1]
    
    # Compute offset matching for each of the 5 possible offsets
    for offset in range(5):
        indices = [offset, offset + 1, offset + 2, offset + 3]
        
        # Apply X gates for negation where pattern bit is 0
        for i, idx in enumerate(indices):
            if pattern[i] == 0:
                qc.x(problem_qubits[idx])
        
        # Apply multi-controlled X to compute AND of all conditions
        controls = [problem_qubits[idx] for idx in indices]
        qc.mcx(controls, ancilla_qubits[offset])
        
        # Un-apply X gates for negation
        for i, idx in enumerate(indices):
            if pattern[i] == 0:
                qc.x(problem_qubits[idx])
    
    # Compute OR of all 5 offset match bits into ancilla_qubits[5]
    # Using the identity: OR(bits) = NOT(AND(NOT bits))
    
    # Negate all offset bits
    for i in range(5):
        qc.x(ancilla_qubits[i])
    
    # AND them together into the result ancilla
    controls = [ancilla_qubits[i] for i in range(5)]
    qc.mcx(controls, ancilla_qubits[5])
    
    # Negate the offset bits back
    for i in range(5):
        qc.x(ancilla_qubits[i])
    
    # Negate the result to get OR
    qc.x(ancilla_qubits[5])
    
    # Apply phase: -1 if result is 1 (mark states where pattern matches)
    qc.z(ancilla_qubits[5])
    
    # Uncompute to return all ancillas to |0>
    
    # Uncompute OR (reverse of OR computation)
    qc.x(ancilla_qubits[5])
    
    for i in range(5):
        qc.x(ancilla_qubits[i])
    
    qc.mcx(controls, ancilla_qubits[5])
    
    for i in range(5):
        qc.x(ancilla_qubits[i])
    
    # Uncompute offset matching (reverse order of offset computation)
    for offset in range(4, -1, -1):
        indices = [offset, offset + 1, offset + 2, offset + 3]
        
        # Un-apply X gates for negation
        for i, idx in enumerate(indices):
            if pattern[i] == 0:
                qc.x(problem_qubits[idx])
        
        # Uncompute multi-controlled X
        controls = [problem_qubits[idx] for idx in indices]
        qc.mcx(controls, ancilla_qubits[offset])
        
        # Apply X gates for negation again
        for i, idx in enumerate(indices):
            if pattern[i] == 0:
                qc.x(problem_qubits[idx])
