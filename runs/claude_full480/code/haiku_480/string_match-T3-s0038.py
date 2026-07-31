from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    
    pattern = [1, 1, 0, 1]  # "1101"
    text_len = 8
    pattern_len = len(pattern)
    num_offsets = text_len - pattern_len + 1  # 5 offsets
    
    match_flags = ancilla_qubits[:num_offsets]
    final_result = ancilla_qubits[num_offsets]
    
    # COMPUTE: Determine if pattern matches at each offset
    for offset in range(num_offsets):
        flag = match_flags[offset]
        q0 = problem_qubits[offset]
        q1 = problem_qubits[offset+1]
        q2 = problem_qubits[offset+2]
        q3 = problem_qubits[offset+3]
        
        # Compute: q0 AND q1 AND q3 AND (NOT q2)
        qc.mcx([q0, q1, q3], flag)
        qc.ccx(flag, q2, flag)
    
    # COMPUTE: Compute OR of match flags
    for flag in match_flags:
        qc.x(flag)
    qc.mcx(match_flags, final_result)
    qc.x(final_result)
    for flag in match_flags:
        qc.x(flag)
    
    # PHASE: Apply Z gate
    qc.z(final_result)
    
    # UNCOMPUTE: Undo OR computation
    for flag in match_flags:
        qc.x(flag)
    qc.x(final_result)
    qc.mcx(match_flags, final_result)
    for flag in match_flags:
        qc.x(flag)
    
    # UNCOMPUTE: Undo match flag computation
    for offset in range(num_offsets - 1, -1, -1):
        flag = match_flags[offset]
        q0 = problem_qubits[offset]
        q1 = problem_qubits[offset+1]
        q2 = problem_qubits[offset+2]
        q3 = problem_qubits[offset+3]
        
        qc.ccx(flag, q2, flag)
        qc.mcx([q0, q1, q3], flag)
