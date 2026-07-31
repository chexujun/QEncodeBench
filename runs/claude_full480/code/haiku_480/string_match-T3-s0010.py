from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Pattern "1110" at offsets 0..4
    offsets = [0, 1, 2, 3, 4]
    match_ancillas = ancilla_qubits[0:5]
    work_qubit = ancilla_qubits[5]
    
    # Phase 1: Compute if pattern matches at each offset
    for idx, offset in enumerate(offsets):
        a = match_ancillas[idx]
        # Check s[offset:offset+4] == "1110"
        # (i.e., s[offset]=1, s[offset+1]=1, s[offset+2]=1, s[offset+3]=0)
        qc.x(problem_qubits[offset+3])
        qc.mcx([problem_qubits[offset], problem_qubits[offset+1], 
                problem_qubits[offset+2], problem_qubits[offset+3]], a)
        qc.x(problem_qubits[offset+3])
    
    # Phase 2: Compute OR of all matches into work_qubit
    # Use De Morgan: OR = NOT(AND(NOT(...)))
    for a in match_ancillas:
        qc.x(a)
    qc.mcx(match_ancillas, work_qubit)
    qc.x(work_qubit)
    for a in match_ancillas:
        qc.x(a)
    
    # Apply phase
    qc.z(work_qubit)
    
    # Uncompute phase 2
    for a in match_ancillas:
        qc.x(a)
    qc.mcx(match_ancillas, work_qubit)
    qc.x(work_qubit)
    for a in match_ancillas:
        qc.x(a)
    
    # Uncompute phase 1 (in reverse order)
    for idx in range(len(offsets)-1, -1, -1):
        offset = offsets[idx]
        a = match_ancillas[idx]
        qc.x(problem_qubits[offset+3])
        qc.mcx([problem_qubits[offset], problem_qubits[offset+1], 
                problem_qubits[offset+2], problem_qubits[offset+3]], a)
        qc.x(problem_qubits[offset+3])
