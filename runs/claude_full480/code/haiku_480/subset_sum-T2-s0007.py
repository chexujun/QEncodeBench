from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    q0, q1, q2, q3 = problem_qubits[0:4]
    ancilla = ancilla_qubits[0]
    
    # Compute: ancilla = (NOT q0) AND (NOT q1) AND q2 AND (NOT q3)
    # This marks the unique state where selected elements sum to 6
    qc.x(q0)
    qc.x(q1)
    qc.x(q3)
    
    # Multi-controlled X: ancilla flips iff all inputs are 1
    qc.mcx([q0, q1, q2, q3], ancilla)
    
    # Apply phase -1 to marked state
    qc.z(ancilla)
    
    # Uncompute: reverse the multi-controlled X
    qc.mcx([q0, q1, q2, q3], ancilla)
    
    # Uncompute: undo the X gates
    qc.x(q3)
    qc.x(q1)
    qc.x(q0)
