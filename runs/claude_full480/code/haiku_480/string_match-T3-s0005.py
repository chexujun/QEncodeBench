from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Pattern "000": check if any 3 consecutive qubits are all 0
    # 6 offsets: 0, 1, 2, 3, 4, 5
    
    match_qubits = ancilla_qubits[0:6]
    result_qubit = ancilla_qubits[6]
    
    # Compute match results for each offset
    for o in range(6):
        qubits = [problem_qubits[o + i] for i in range(3)]
        match_qubit = match_qubits[o]
        
        # Set match_qubit = 1 iff all three problem qubits are 0
        # (by flipping qubits, checking if all are 1, then restoring)
        for q in qubits:
            qc.x(q)
        qc.mcx(qubits, match_qubit)
        for q in qubits:
            qc.x(q)
    
    # Compute OR of all match results into result_qubit
    # Using De Morgan: OR = NOT(AND of NOTs)
    for m in match_qubits:
        qc.x(m)
    
    qc.mcx(match_qubits, result_qubit)
    
    for m in match_qubits:
        qc.x(m)
    
    qc.x(result_qubit)
    
    # Apply phase -1 when pattern matches (result_qubit = 1)
    qc.z(result_qubit)
    
    # Uncompute OR result
    qc.x(result_qubit)
    
    for m in match_qubits:
        qc.x(m)
    
    qc.mcx(match_qubits, result_qubit)
    
    for m in match_qubits:
        qc.x(m)
    
    # Uncompute match results (reverse order)
    for o in range(5, -1, -1):
        qubits = [problem_qubits[o + i] for i in range(3)]
        match_qubit = match_qubits[o]
        
        for q in qubits:
            qc.x(q)
        qc.mcx(qubits, match_qubit)
        for q in qubits:
            qc.x(q)
