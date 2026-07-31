from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    s = problem_qubits  # 8-bit text
    flags = ancilla_qubits[:5]  # One flag per offset
    result = ancilla_qubits[5]  # Combined OR result
    
    # Compute: For each offset, AND the 4 consecutive bits
    for offset in range(5):
        controls = [s[offset], s[offset+1], s[offset+2], s[offset+3]]
        qc.mcx(controls, flags[offset])
    
    # Compute OR of all flags into result using De Morgan: OR(a,b,c,d,e) = NOT(AND(NOT a, NOT b, NOT c, NOT d, NOT e))
    # Flip all flags
    for f in flags:
        qc.x(f)
    
    # AND of flipped flags into result
    qc.mcx(flags, result)
    
    # Flip result to get OR
    qc.x(result)
    
    # Apply phase
    qc.z(result)
    
    # Uncompute: reverse all steps
    qc.x(result)
    qc.mcx(flags, result)
    for f in flags:
        qc.x(f)
    
    # Uncompute the offset ANDs
    for offset in range(5):
        controls = [s[offset], s[offset+1], s[offset+2], s[offset+3]]
        qc.mcx(controls, flags[offset])
