from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Extract problem qubits for the two free cells
    # Free cell 0 (row 1, col 1): bits problem_qubits[0], problem_qubits[1]
    # Free cell 1 (row 1, col 2): bits problem_qubits[2], problem_qubits[3]
    b0_0 = problem_qubits[0]
    b1_0 = problem_qubits[1]
    b0_1 = problem_qubits[2]
    b1_1 = problem_qubits[3]
    
    # Use first three ancillas
    a0 = ancilla_qubits[0]
    a1 = ancilla_qubits[1]
    a2 = ancilla_qubits[2]
    
    # COMPUTE PHASE: The unique solution is cell(1,1) = 0 and cell(1,2) = 1
    
    # Check cell 1 = 1: requires code 01, i.e., b0_1=1 AND b1_1=0
    # Compute a1 = b0_1 AND NOT(b1_1)
    qc.x(b1_1)
    qc.ccx(b0_1, b1_1, a1)
    qc.x(b1_1)
    
    # Check cell 0 = 0: requires codes 00 or 11, i.e., b0_0 == b1_0
    # Compute a0 = NOT(b0_0 XOR b1_0)
    qc.cx(b0_0, a0)
    qc.cx(b1_0, a0)
    qc.x(a0)
    
    # Combine: a2 = 1 iff both conditions met
    qc.ccx(a0, a1, a2)
    
    # PHASE: apply -1 to marked states
    qc.z(a2)
    
    # UNCOMPUTE: return ancillas to |0⟩ while preserving phase
    qc.ccx(a0, a1, a2)
    
    qc.x(a0)
    qc.cx(b1_0, a0)
    qc.cx(b0_0, a0)
    
    qc.x(b1_1)
    qc.ccx(b0_1, b1_1, a1)
    qc.x(b1_1)
