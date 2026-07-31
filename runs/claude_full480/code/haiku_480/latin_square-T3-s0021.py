from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    c0, c1, c2, c3 = ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[2], ancilla_qubits[3]
    result = ancilla_qubits[4]
    
    # Compute constraint 0: cell (0,0) value = 0
    qc.cx(problem_qubits[0], c0)
    qc.cx(problem_qubits[1], c0)
    qc.x(c0)
    
    # Compute constraint 1: cell (1,0) value = 2
    qc.x(problem_qubits[2])
    qc.ccx(problem_qubits[2], problem_qubits[3], c1)
    qc.x(problem_qubits[2])
    
    # Compute constraint 2: cell (2,1) value = 2
    qc.x(problem_qubits[4])
    qc.ccx(problem_qubits[4], problem_qubits[5], c2)
    qc.x(problem_qubits[4])
    
    # Compute constraint 3: cell (2,2) value = 0
    qc.cx(problem_qubits[6], c3)
    qc.cx(problem_qubits[7], c3)
    qc.x(c3)
    
    # Compute AND of all constraints
    qc.mcx([c0, c1, c2, c3], result)
    
    # Apply phase
    qc.z(result)
    
    # Uncompute AND
    qc.mcx([c0, c1, c2, c3], result)
    
    # Undo constraint 3
    qc.x(c3)
    qc.cx(problem_qubits[7], c3)
    qc.cx(problem_qubits[6], c3)
    
    # Undo constraint 2
    qc.x(problem_qubits[4])
    qc.ccx(problem_qubits[4], problem_qubits[5], c2)
    qc.x(problem_qubits[4])
    
    # Undo constraint 1
    qc.x(problem_qubits[2])
    qc.ccx(problem_qubits[2], problem_qubits[3], c1)
    qc.x(problem_qubits[2])
    
    # Undo constraint 0
    qc.x(c0)
    qc.cx(problem_qubits[1], c0)
    qc.cx(problem_qubits[0], c0)
