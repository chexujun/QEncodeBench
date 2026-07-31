from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Compute pattern matches for each possible offset (0-4)
    # For each offset, check if all 4 consecutive bits are 0
    offsets = [0, 1, 2, 3, 4]
    for idx, offset in enumerate(offsets):
        # Flip qubits to prepare for zero detection (X: |0> -> |1>)
        for i in range(4):
            qc.x(problem_qubits[offset + i])
        # AND the four bits into ancilla[idx]
        qc.mcx(
            [problem_qubits[offset + i] for i in range(4)],
            ancilla_qubits[idx]
        )
        # Flip back to restore problem qubits
        for i in range(4):
            qc.x(problem_qubits[offset + i])
    
    # Compute OR of all matches into ancilla[5]
    match_qubits = [ancilla_qubits[i] for i in range(5)]
    result_qubit = ancilla_qubits[5]
    
    # OR computation using: OR = NOT(AND(NOTs))
    # Flip all matches to prepare for AND of inverted values
    for mq in match_qubits:
        qc.x(mq)
    # Compute AND of flipped matches into result
    qc.mcx(match_qubits, result_qubit)
    # Flip back
    for mq in match_qubits:
        qc.x(mq)
    # Flip result to complete OR formula
    qc.x(result_qubit)
    
    # Apply phase -1 for solutions
    qc.z(result_qubit)
    
    # Uncompute OR (reverse order)
    qc.x(result_qubit)
    for mq in match_qubits:
        qc.x(mq)
    qc.mcx(match_qubits, result_qubit)
    for mq in match_qubits:
        qc.x(mq)
    
    # Uncompute matches
    for idx, offset in enumerate(offsets):
        for i in range(4):
            qc.x(problem_qubits[offset + i])
        qc.mcx(
            [problem_qubits[offset + i] for i in range(4)],
            ancilla_qubits[idx]
        )
        for i in range(4):
            qc.x(problem_qubits[offset + i])
