from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Pattern "00?1" matches at offset o if:
    # s_o == 0 AND s_(o+1) == 0 AND s_(o+3) == 1
    # Offsets to check: 0, 1, 2, 3, 4
    
    # Use ancillas for computation
    temp_a = ancilla_qubits[0]        # for s_i == 0 checks
    temp_b = ancilla_qubits[1]        # for s_i == 0 checks
    temp_and = ancilla_qubits[2]      # for AND computation
    temp_match = ancilla_qubits[3]    # for current offset match
    temp_nots = ancilla_qubits[4]     # accumulates AND(NOT(conditions))
    result = ancilla_qubits[5]        # helper for AND operations
    
    # Forward pass: compute AND of NOT(all conditions)
    # This equals NOT(OR of all conditions) by De Morgan's law
    qc.x(temp_nots)  # Initialize to 1
    
    for offset in range(5):
        # Compute condition at this offset into temp_match
        # Condition: s_offset == 0 AND s_(offset+1) == 0 AND s_(offset+3) == 1
        
        # Check s_offset == 0
        qc.x(temp_a)
        qc.cx(problem_qubits[offset], temp_a)  # temp_a = NOT(s_offset)
        
        # Check s_(offset+1) == 0
        qc.x(temp_b)
        qc.cx(problem_qubits[offset+1], temp_b)  # temp_b = NOT(s_(offset+1))
        
        # Compute AND of the two checks
        qc.ccx(temp_a, temp_b, temp_and)  # temp_and = temp_a AND temp_b
        
        # AND with s_(offset+3) == 1 (direct qubit check)
        qc.ccx(temp_and, problem_qubits[offset+3], temp_match)
        
        # Update temp_nots: temp_nots = temp_nots AND NOT(temp_match)
        qc.x(temp_match)
        qc.ccx(temp_match, temp_nots, result)
        qc.cx(result, temp_nots)
        qc.x(result)
        qc.x(temp_match)
        
        # Uncompute temporary values
        qc.ccx(temp_and, problem_qubits[offset+3], temp_match)
        qc.ccx(temp_a, temp_b, temp_and)
        qc.cx(problem_qubits[offset+1], temp_b)
        qc.x(temp_b)
        qc.cx(problem_qubits[offset], temp_a)
        qc.x(temp_a)
    
    # Flip to get OR (by De Morgan)
    qc.x(temp_nots)
    
    # Apply phase
    qc.z(temp_nots)
    
    # Backward pass: uncompute the OR
    qc.x(temp_nots)
    
    for offset in range(4, -1, -1):
        # Recompute condition
        qc.x(temp_a)
        qc.cx(problem_qubits[offset], temp_a)
        qc.x(temp_b)
        qc.cx(problem_qubits[offset+1], temp_b)
        qc.ccx(temp_a, temp_b, temp_and)
        qc.ccx(temp_and, problem_qubits[offset+3], temp_match)
        
        # Undo AND of NOTs update
        qc.x(temp_match)
        qc.ccx(temp_match, temp_nots, result)
        qc.cx(result, temp_nots)
        qc.x(result)
        qc.x(temp_match)
        
        # Uncompute
        qc.ccx(temp_and, problem_qubits[offset+3], temp_match)
        qc.ccx(temp_a, temp_b, temp_and)
        qc.cx(problem_qubits[offset+1], temp_b)
        qc.x(temp_b)
        qc.cx(problem_qubits[offset], temp_a)
        qc.x(temp_a)
