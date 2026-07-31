from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Pattern: "1001" at offsets 0, 1, 2, 3, 4
    offsets = [0, 1, 2, 3, 4]
    n_offsets = len(offsets)
    
    # Allocate ancillas
    match_ancillas = ancilla_qubits[:n_offsets]
    result_ancilla = ancilla_qubits[n_offsets]
    
    # Compute match conditions for each offset
    for idx, offset in enumerate(offsets):
        match_anc = match_ancillas[idx]
        qubits = [problem_qubits[offset + i] for i in range(4)]
        
        # Check: s[offset]=1, s[offset+1]=0, s[offset+2]=0, s[offset+3]=1
        qc.x(qubits[1])
        qc.x(qubits[2])
        qc.mcx(qubits, match_anc)
        qc.x(qubits[1])
        qc.x(qubits[2])
    
    # Compute OR of match conditions using De Morgan: OR = NOT(AND(NOT ...))
    for i in range(n_offsets):
        qc.x(match_ancillas[i])
    qc.mcx(match_ancillas, result_ancilla)
    qc.x(result_ancilla)
    for i in range(n_offsets):
        qc.x(match_ancillas[i])
    
    # Apply phase
    qc.z(result_ancilla)
    
    # Uncompute OR
    for i in range(n_offsets):
        qc.x(match_ancillas[i])
    qc.mcx(match_ancillas, result_ancilla)
    qc.x(result_ancilla)
    for i in range(n_offsets):
        qc.x(match_ancillas[i])
    
    # Uncompute match conditions
    for idx in range(n_offsets - 1, -1, -1):
        offset = offsets[idx]
        match_anc = match_ancillas[idx]
        qubits = [problem_qubits[offset + i] for i in range(4)]
        
        qc.x(qubits[1])
        qc.x(qubits[2])
        qc.mcx(qubits, match_anc)
        qc.x(qubits[1])
        qc.x(qubits[2])
