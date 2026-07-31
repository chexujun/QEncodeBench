from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a0 = ancilla_qubits[0]  # result for offset 0
    a1 = ancilla_qubits[1]  # result for offset 1
    a2 = ancilla_qubits[2]  # OR of a0 and a1
    
    # Compute offset 0 match: s_0=1 AND s_1=1 AND s_2=0 AND s_3=1 AND s_4=1
    # Flip s_2 to check for equality to 0
    qc.x(problem_qubits[2])
    qc.mcx([problem_qubits[0], problem_qubits[1], problem_qubits[2], 
            problem_qubits[3], problem_qubits[4]], a0)
    qc.x(problem_qubits[2])
    
    # Compute offset 1 match: s_1=1 AND s_2=1 AND s_3=0 AND s_4=1 AND s_5=1
    # Flip s_3 to check for equality to 0
    qc.x(problem_qubits[3])
    qc.mcx([problem_qubits[1], problem_qubits[2], problem_qubits[3], 
            problem_qubits[4], problem_qubits[5]], a1)
    qc.x(problem_qubits[3])
    
    # Compute OR: a2 = a0 OR a1 using NOT(NOT a0 AND NOT a1)
    qc.x(a0)
    qc.x(a1)
    qc.ccx(a0, a1, a2)
    qc.x(a2)
    qc.x(a1)
    qc.x(a0)
    
    # Apply phase flip
    qc.z(a2)
    
    # Uncompute OR
    qc.x(a0)
    qc.x(a1)
    qc.x(a2)
    qc.ccx(a0, a1, a2)
    qc.x(a1)
    qc.x(a0)
    
    # Uncompute offset 1
    qc.x(problem_qubits[3])
    qc.mcx([problem_qubits[1], problem_qubits[2], problem_qubits[3], 
            problem_qubits[4], problem_qubits[5]], a1)
    qc.x(problem_qubits[3])
    
    # Uncompute offset 0
    qc.x(problem_qubits[2])
    qc.mcx([problem_qubits[0], problem_qubits[1], problem_qubits[2], 
            problem_qubits[3], problem_qubits[4]], a0)
    qc.x(problem_qubits[2])
