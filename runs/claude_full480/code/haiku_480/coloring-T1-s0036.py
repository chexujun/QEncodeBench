from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a0 = ancilla_qubits[0]
    a1 = ancilla_qubits[1]
    a2 = ancilla_qubits[2]
    a3 = ancilla_qubits[3]
    
    # Compute constraint 1 (edge 0-1): q0 XOR q1 XOR q2 XOR q3 = 1
    qc.cx(problem_qubits[0], a0)
    qc.cx(problem_qubits[1], a0)
    qc.cx(problem_qubits[2], a0)
    qc.cx(problem_qubits[3], a0)
    
    # Compute constraint 2 (edge 0-2): q0 XOR q1 XOR q4 XOR q5 = 1
    qc.cx(problem_qubits[0], a1)
    qc.cx(problem_qubits[1], a1)
    qc.cx(problem_qubits[4], a1)
    qc.cx(problem_qubits[5], a1)
    
    # Compute constraint 3 (edge 2-3): q4 XOR q5 XOR q6 XOR q7 = 1
    qc.cx(problem_qubits[4], a2)
    qc.cx(problem_qubits[5], a2)
    qc.cx(problem_qubits[6], a2)
    qc.cx(problem_qubits[7], a2)
    
    # Compute AND(constraint1, constraint2) into a3
    qc.ccx(a0, a1, a3)
    
    # Apply phase if AND(constraint1, constraint2) AND constraint3
    qc.cz(a3, a2)
    
    # Uncompute AND
    qc.ccx(a0, a1, a3)
    
    # Uncompute constraint 3
    qc.cx(problem_qubits[7], a2)
    qc.cx(problem_qubits[6], a2)
    qc.cx(problem_qubits[5], a2)
    qc.cx(problem_qubits[4], a2)
    
    # Uncompute constraint 2
    qc.cx(problem_qubits[5], a1)
    qc.cx(problem_qubits[4], a1)
    qc.cx(problem_qubits[1], a1)
    qc.cx(problem_qubits[0], a1)
    
    # Uncompute constraint 1
    qc.cx(problem_qubits[3], a0)
    qc.cx(problem_qubits[2], a0)
    qc.cx(problem_qubits[1], a0)
    qc.cx(problem_qubits[0], a0)
