from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Extract ancilla indices
    a0, a1, a2, a3, a4 = ancilla_qubits[:5]
    
    # Constraint 1: Free cell 0 must be 0 (code 00 or 11)
    # Equivalent to: problem_qubits[0] = problem_qubits[1]
    qc.cx(problem_qubits[0], a0)
    qc.cx(problem_qubits[1], a0)
    qc.x(a0)
    
    # Constraint 2: Free cell 1 must be 1 (code 01)
    # Equivalent to: problem_qubits[2] = 1 AND problem_qubits[3] = 0
    qc.x(problem_qubits[3])
    qc.ccx(problem_qubits[2], problem_qubits[3], a1)
    qc.x(problem_qubits[3])
    
    # Constraint 3: Free cell 2 must be 2 (code 10)
    # Equivalent to: problem_qubits[4] = 0 AND problem_qubits[5] = 1
    qc.x(problem_qubits[4])
    qc.ccx(problem_qubits[4], problem_qubits[5], a2)
    qc.x(problem_qubits[4])
    
    # Constraint 4: Free cell 3 must be 0 (code 00 or 11)
    # Equivalent to: problem_qubits[6] = problem_qubits[7]
    qc.cx(problem_qubits[6], a3)
    qc.cx(problem_qubits[7], a3)
    qc.x(a3)
    
    # Compute AND of all constraints
    qc.mcx([a0, a1, a2, a3], a4)
    
    # Apply phase -1 when a4 = 1
    qc.z(a4)
    
    # Uncompute: reverse the AND computation
    qc.mcx([a0, a1, a2, a3], a4)
    
    # Uncompute constraint 4
    qc.x(a3)
    qc.cx(problem_qubits[7], a3)
    qc.cx(problem_qubits[6], a3)
    
    # Uncompute constraint 3
    qc.x(problem_qubits[4])
    qc.ccx(problem_qubits[4], problem_qubits[5], a2)
    qc.x(problem_qubits[4])
    
    # Uncompute constraint 2
    qc.x(problem_qubits[3])
    qc.ccx(problem_qubits[2], problem_qubits[3], a1)
    qc.x(problem_qubits[3])
    
    # Uncompute constraint 1
    qc.x(a0)
    qc.cx(problem_qubits[1], a0)
    qc.cx(problem_qubits[0], a0)
