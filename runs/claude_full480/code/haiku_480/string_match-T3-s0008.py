from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    
    # Compute pattern match at each offset into ancilla_qubits[0..4]
    # Pattern "11?0" matches at offset o if: s_o=1 AND s_{o+1}=1 AND s_{o+3}=0
    for offset in range(5):
        s_o = problem_qubits[offset]
        s_o1 = problem_qubits[offset + 1]
        s_o3 = problem_qubits[offset + 3]
        match_anc = ancilla_qubits[offset]
        
        # Compute the match condition into match_anc
        # Flip s_o3 to handle the NOT(s_o3) part
        qc.x(s_o3)
        # Multi-controlled X: match_anc ⊕= (s_o AND s_o1 AND NOT(s_o3))
        qc.mcx([s_o, s_o1, s_o3], match_anc)
        # Flip s_o3 back to its original state
        qc.x(s_o3)
    
    # Compute OR of all match conditions into ancilla_qubits[5]
    result_anc = ancilla_qubits[5]
    
    # Copy first match to result
    qc.cx(ancilla_qubits[0], result_anc)
    
    # Iteratively OR in remaining matches
    # Using formula: result = result OR match = result ⊕ (match AND NOT(result))
    for i in range(1, 5):
        match_anc = ancilla_qubits[i]
        qc.x(result_anc)  # Flip to NOT(result_anc)
        qc.mcx([match_anc, result_anc], result_anc)  # result_anc ⊕= match_anc AND (flipped result_anc)
        qc.x(result_anc)  # Flip back
    
    # Apply phase -1 (via Z gate on the result qubit)
    qc.z(result_anc)
    
    # Uncompute in reverse order
    # Reverse the OR operations
    for i in range(4, 0, -1):
        match_anc = ancilla_qubits[i]
        qc.x(result_anc)
        qc.mcx([match_anc, result_anc], result_anc)
        qc.x(result_anc)
    
    # Reverse the copy operation
    qc.cx(ancilla_qubits[0], result_anc)
    
    # Reverse the match computations
    for offset in range(4, -1, -1):
        s_o = problem_qubits[offset]
        s_o1 = problem_qubits[offset + 1]
        s_o3 = problem_qubits[offset + 3]
        match_anc = ancilla_qubits[offset]
        
        qc.x(s_o3)
        qc.mcx([s_o, s_o1, s_o3], match_anc)
        qc.x(s_o3)
