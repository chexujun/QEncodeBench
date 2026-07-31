from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Oracle for minimum vertex cover of size <= 2
    # Graph edges: (0,1), (0,2), (0,3), (0,4), (2,4)
    # Valid covers of size <= 2: {0,2} and {0,4}
    # Predicate: x_0 AND NOT(x_1) AND NOT(x_3) AND (x_2 XOR x_4)
    
    # Compute x_2 XOR x_4 into ancilla
    a1 = ancilla_qubits[0]
    qc.cx(problem_qubits[2], a1)
    qc.cx(problem_qubits[4], a1)
    
    # Compute the full predicate: x_0 AND NOT(x_1) AND NOT(x_3) AND a1
    a2 = ancilla_qubits[1]
    
    # Flip x_1 and x_3 to compute NOT values
    qc.x(problem_qubits[1])
    qc.x(problem_qubits[3])
    
    # Multi-controlled-X to compute AND into a2
    qc.mcx([problem_qubits[0], problem_qubits[1], problem_qubits[3], a1], a2)
    
    # Apply phase flip for marked states
    qc.z(a2)
    
    # Uncompute a2
    qc.mcx([problem_qubits[0], problem_qubits[1], problem_qubits[3], a1], a2)
    
    # Uncompute the X gates
    qc.x(problem_qubits[3])
    qc.x(problem_qubits[1])
    
    # Uncompute a1
    qc.cx(problem_qubits[4], a1)
    qc.cx(problem_qubits[2], a1)
