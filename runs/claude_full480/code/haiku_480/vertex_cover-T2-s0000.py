from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # The only valid vertex cover of size <= 2 is {0, 3}
    # This corresponds to x = [1, 0, 0, 1, 0] in binary (little-endian)
    
    match_ancilla = ancilla_qubits[0]
    
    # Invert bits that should be 0 in the target pattern 01001
    qc.x(problem_qubits[1])
    qc.x(problem_qubits[2])
    qc.x(problem_qubits[4])
    
    # Compute: match_ancilla = 1 iff all controls are 1 (pattern matched)
    qc.mcx([problem_qubits[0], problem_qubits[1], problem_qubits[2], 
            problem_qubits[3], problem_qubits[4]], match_ancilla)
    
    # Un-invert bits
    qc.x(problem_qubits[4])
    qc.x(problem_qubits[2])
    qc.x(problem_qubits[1])
    
    # Apply phase -1 to marked state
    qc.z(match_ancilla)
    
    # Uncompute: restore match_ancilla to |0>
    qc.x(problem_qubits[1])
    qc.x(problem_qubits[2])
    qc.x(problem_qubits[4])
    qc.mcx([problem_qubits[0], problem_qubits[1], problem_qubits[2], 
            problem_qubits[3], problem_qubits[4]], match_ancilla)
    qc.x(problem_qubits[4])
    qc.x(problem_qubits[2])
    qc.x(problem_qubits[1])
