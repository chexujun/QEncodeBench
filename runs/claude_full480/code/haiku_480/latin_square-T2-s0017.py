from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    """
    Oracle for 3x3 Latin square completion via Grover's algorithm.
    
    The unique valid completion requires:
    - Free cell (0,0) = value 1 (code 01)
    - Free cell (1,0) = value 0 (code 00)
    - Free cell (2,2) = value 1 (code 01)
    
    This oracle applies phase -1 only to that state.
    """
    b0_0, b1_0, b0_1, b1_1, b0_2, b1_2 = problem_qubits
    flag = ancilla_qubits[0]
    
    # Flip qubits that must be 0 in the target state so all controls are 1
    qc.x(b1_0)
    qc.x(b0_1)
    qc.x(b1_1)
    qc.x(b1_2)
    
    # Multi-controlled X: set flag=1 only if all controls are 1
    qc.mcx([b0_0, b1_0, b0_1, b1_1, b0_2, b1_2], flag)
    
    # Apply phase: Z on flag applies -1 phase if flag=1
    qc.z(flag)
    
    # Uncompute: restore flag to 0
    qc.mcx([b0_0, b1_0, b0_1, b1_1, b0_2, b1_2], flag)
    
    # Restore problem qubits
    qc.x(b1_0)
    qc.x(b0_1)
    qc.x(b1_1)
    qc.x(b1_2)
