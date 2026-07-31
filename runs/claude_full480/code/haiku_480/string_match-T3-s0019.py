from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Compute match(o) for each offset o in 0..4
    # match(o) = (s_o == 1) AND (s_(o+1) == 0) AND (s_(o+2) == 1)
    for offset in range(5):
        q0 = problem_qubits[offset]
        q1 = problem_qubits[offset + 1]
        q2 = problem_qubits[offset + 2]
        result = ancilla_qubits[offset]
        
        qc.x(q1)  # Flip q1 to check if it equals 0
        qc.mcx([q0, q1, q2], result)  # Compute AND into result
        qc.x(q1)  # Flip q1 back
    
    # Compute OR of all matches using de Morgan's law
    # OR(a0,a1,a2,a3,a4) = NOT(AND(NOT a0, NOT a1, NOT a2, NOT a3, NOT a4))
    match_ancillas = ancilla_qubits[:5]
    or_result = ancilla_qubits[5]
    
    # Flip all match ancillas
    for a in match_ancillas:
        qc.x(a)
    # Compute AND of flipped values
    qc.mcx(match_ancillas, or_result)
    # Flip match ancillas back
    for a in match_ancillas:
        qc.x(a)
    # Flip result to convert AND to OR
    qc.x(or_result)
    
    # Apply phase -1 if pattern matches
    qc.z(or_result)
    
    # Uncompute: reverse the OR computation
    qc.x(or_result)
    for a in match_ancillas:
        qc.x(a)
    qc.mcx(match_ancillas, or_result)
    for a in match_ancillas:
        qc.x(a)
    
    # Uncompute matches in reverse order
    for offset in reversed(range(5)):
        q0 = problem_qubits[offset]
        q1 = problem_qubits[offset + 1]
        q2 = problem_qubits[offset + 2]
        result = ancilla_qubits[offset]
        
        qc.x(q1)
        qc.mcx([q0, q1, q2], result)
        qc.x(q1)
