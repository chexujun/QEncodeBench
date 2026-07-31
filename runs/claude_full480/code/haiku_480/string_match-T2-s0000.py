from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a0, a1, a2 = ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[2]
    
    # Compute offset 0 match into a0
    # Pattern "0011?" at text[0:5]
    # Check: s[0]==0, s[1]==0, s[2]==1, s[3]==1
    qc.x(problem_qubits[0])
    qc.x(problem_qubits[1])
    qc.mcx([problem_qubits[0], problem_qubits[1], problem_qubits[2], problem_qubits[3]], a0)
    qc.x(problem_qubits[0])
    qc.x(problem_qubits[1])
    
    # Compute offset 1 match into a1
    # Pattern "0011?" at text[1:6]
    # Check: s[1]==0, s[2]==0, s[3]==1, s[4]==1
    qc.x(problem_qubits[1])
    qc.x(problem_qubits[2])
    qc.mcx([problem_qubits[1], problem_qubits[2], problem_qubits[3], problem_qubits[4]], a1)
    qc.x(problem_qubits[1])
    qc.x(problem_qubits[2])
    
    # Compute a0 OR a1 into a2 using: a0 OR a1 = a0 XOR a1 XOR (a0 AND a1)
    qc.ccx(a0, a1, a2)
    qc.cx(a0, a2)
    qc.cx(a1, a2)
    
    # Apply phase -1
    qc.z(a2)
    
    # Uncompute a2 (reverse order)
    qc.cx(a1, a2)
    qc.cx(a0, a2)
    qc.ccx(a0, a1, a2)
    
    # Uncompute a1
    qc.x(problem_qubits[1])
    qc.x(problem_qubits[2])
    qc.mcx([problem_qubits[1], problem_qubits[2], problem_qubits[3], problem_qubits[4]], a1)
    qc.x(problem_qubits[1])
    qc.x(problem_qubits[2])
    
    # Uncompute a0
    qc.x(problem_qubits[0])
    qc.x(problem_qubits[1])
    qc.mcx([problem_qubits[0], problem_qubits[1], problem_qubits[2], problem_qubits[3]], a0)
    qc.x(problem_qubits[0])
    qc.x(problem_qubits[1])
