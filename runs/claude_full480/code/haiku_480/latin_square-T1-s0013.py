from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Extract problem qubits for free cells
    b0_0, b1_0, b0_1, b1_1 = problem_qubits[0:4]
    
    # Extract ancilla qubits
    a_c0 = ancilla_qubits[0]      # Holds b0_0 AND NOT b1_0 (free cell 0 = 1)
    a_c1 = ancilla_qubits[1]      # Holds NOT(b0_1 XOR b1_1) (free cell 1 = 0)
    result = ancilla_qubits[2]    # Holds overall predicate (both constraints)
    
    # COMPUTE PHASE
    
    # Compute a_c0 = b0_0 AND NOT b1_0
    # Checks: free cell 0 must have value 1 (code = 01)
    qc.x(b1_0)
    qc.ccx(b0_0, b1_0, a_c0)
    qc.x(b1_0)
    
    # Compute a_c1 = NOT(b0_1 XOR b1_1) = b0_1 XNOR b1_1
    # Checks: free cell 1 must have value 0 (code in {00, 11})
    qc.cx(b0_1, a_c1)
    qc.cx(b1_1, a_c1)
    qc.x(a_c1)
    
    # Compute result = a_c0 AND a_c1 (both constraints satisfied)
    qc.ccx(a_c0, a_c1, result)
    
    # APPLY PHASE
    qc.z(result)
    
    # UNCOMPUTE (reverse order, self-inverse operations)
    
    # Uncompute result
    qc.ccx(a_c0, a_c1, result)
    
    # Uncompute a_c1
    qc.x(a_c1)
    qc.cx(b1_1, a_c1)
    qc.cx(b0_1, a_c1)
    
    # Uncompute a_c0
    qc.x(b1_0)
    qc.ccx(b0_0, b1_0, a_c0)
    qc.x(b1_0)
