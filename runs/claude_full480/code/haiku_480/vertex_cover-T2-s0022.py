from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x = problem_qubits
    a = ancilla_qubits
    
    xor_02 = a[0]
    not_x3 = a[1]
    not_x1 = a[2]
    temp_04 = a[3]
    temp_043 = a[4]
    final = a[5]
    
    # COMPUTE: Build the predicate x4 AND NOT x3 AND NOT x1 AND (x0 XOR x2)
    # This marks exactly the vertex covers {0,4} and {2,4}
    qc.cx(x[0], xor_02)
    qc.cx(x[2], xor_02)
    
    qc.x(not_x3)
    qc.cx(x[3], not_x3)
    
    qc.x(not_x1)
    qc.cx(x[1], not_x1)
    
    qc.ccx(x[4], xor_02, temp_04)
    qc.ccx(temp_04, not_x3, temp_043)
    qc.ccx(temp_043, not_x1, final)
    
    # PHASE: Apply -1 phase to marked states
    qc.z(final)
    
    # UNCOMPUTE: Reverse operations to restore ancillas to |0>
    qc.ccx(temp_043, not_x1, final)
    qc.ccx(temp_04, not_x3, temp_043)
    qc.ccx(x[4], xor_02, temp_04)
    
    qc.cx(x[1], not_x1)
    qc.x(not_x1)
    
    qc.cx(x[3], not_x3)
    qc.x(not_x3)
    
    qc.cx(x[2], xor_02)
    qc.cx(x[0], xor_02)
