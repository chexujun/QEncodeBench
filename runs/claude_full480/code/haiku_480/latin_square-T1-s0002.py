from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Extract qubit indices for the two free cells at (0,0) and (0,1)
    b0_0 = problem_qubits[0]  # Free cell 0, low bit
    b1_0 = problem_qubits[1]  # Free cell 0, high bit
    b0_1 = problem_qubits[2]  # Free cell 1, low bit
    b1_1 = problem_qubits[3]  # Free cell 1, high bit
    
    # Ancilla qubits for compute-phase-uncompute pattern
    a0 = ancilla_qubits[0]
    a1 = ancilla_qubits[1]
    a2 = ancilla_qubits[2]
    
    # COMPUTE: a0 = (NOT b0_0) AND b1_0
    # Detects code 10 (value = 0 + 2*1 = 2) for cell 0
    qc.x(b0_0)
    qc.ccx(b0_0, b1_0, a0)
    qc.x(b0_0)
    
    # COMPUTE: a1 = NOT (b0_1 XOR b1_1)
    # Detects codes 00 and 11 (both decode to value 0) for cell 1
    qc.cx(b0_1, a1)
    qc.cx(b1_1, a1)
    qc.x(a1)
    
    # COMPUTE: a2 = a0 AND a1
    # True only when both cell 0 has value 2 and cell 1 has value 0
    qc.ccx(a0, a1, a2)
    
    # PHASE: Apply -1 when both Latin square constraints are satisfied
    qc.z(a2)
    
    # UNCOMPUTE: Restore all ancillas to |0> (reverse of compute)
    qc.ccx(a0, a1, a2)
    qc.x(a1)
    qc.cx(b1_1, a1)
    qc.cx(b0_1, a1)
    qc.x(b0_0)
    qc.ccx(b0_0, b1_0, a0)
    qc.x(b0_0)
