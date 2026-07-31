from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Problem qubits: 6 total (3 cells × 2 bits each)
    c0_b0, c0_b1 = problem_qubits[0], problem_qubits[1]  # Cell 0
    c1_b0, c1_b1 = problem_qubits[2], problem_qubits[3]  # Cell 1
    c2_b0, c2_b1 = problem_qubits[4], problem_qubits[5]  # Cell 2
    
    # Ancilla qubits for computation
    a0 = ancilla_qubits[0]  # Condition: c0 = 0 (b0 XNOR b1)
    a1 = ancilla_qubits[1]  # Condition: c1 = 0 (b0 XNOR b1)
    a2 = ancilla_qubits[2]  # Condition: c2 = 1 (b0=1 AND b1=0)
    a3 = ancilla_qubits[3]  # Intermediate: c0 AND c1
    a4 = ancilla_qubits[4]  # Final: c0 AND c1 AND c2
    
    # COMPUTE: Build conditions for valid Latin square
    
    # Condition 1: c0 = 0 (code is 00 or 11, i.e., b0 XNOR b1 = 1)
    qc.cx(c0_b0, a0)
    qc.cx(c0_b1, a0)
    qc.x(a0)  # Negate to get XNOR
    
    # Condition 2: c1 = 0 (code is 00 or 11, i.e., b0 XNOR b1 = 1)
    qc.cx(c1_b0, a1)
    qc.cx(c1_b1, a1)
    qc.x(a1)  # Negate to get XNOR
    
    # Condition 3: c2 = 1 (code is 01, i.e., b0=1 AND b1=0)
    qc.x(c2_b1)  # Temporarily flip b1 to work with NOT(b1)
    qc.ccx(c2_b0, c2_b1, a2)  # Compute b0 AND NOT(b1)
    qc.x(c2_b1)  # Restore b1
    
    # Combine conditions via conjunction (AND)
    qc.ccx(a0, a1, a3)  # a3 = a0 AND a1
    qc.ccx(a3, a2, a4)  # a4 = a0 AND a1 AND a2
    
    # APPLY PHASE
    qc.z(a4)  # Apply phase -1 when f(x) = 1 (i.e., when a4 = 1)
    
    # UNCOMPUTE: Restore all ancillas to |0⟩
    
    # Reverse the conjunction computations
    qc.ccx(a3, a2, a4)
    qc.ccx(a0, a1, a3)
    
    # Reverse condition 3 computation
    qc.x(c2_b1)
    qc.ccx(c2_b0, c2_b1, a2)
    qc.x(c2_b1)
    
    # Reverse condition 2 computation
    qc.x(a1)
    qc.cx(c1_b1, a1)
    qc.cx(c1_b0, a1)
    
    # Reverse condition 1 computation
    qc.x(a0)
    qc.cx(c0_b1, a0)
    qc.cx(c0_b0, a0)
