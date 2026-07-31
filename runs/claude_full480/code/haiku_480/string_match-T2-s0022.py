from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Pattern "?001?" at offsets 0, 1, 2 over length-7 binary string
    # Offset 0: s_1=0, s_2=0, s_3=1
    # Offset 1: s_2=0, s_3=0, s_4=1
    # Offset 2: s_3=0, s_4=0, s_5=1
    
    a0 = ancilla_qubits[0]
    a1 = ancilla_qubits[1]
    a2 = ancilla_qubits[2]
    result = ancilla_qubits[3]
    
    # Compute offset 0: a0 = (NOT s_1) AND (NOT s_2) AND s_3
    qc.x(problem_qubits[1])
    qc.x(problem_qubits[2])
    qc.mcx([problem_qubits[1], problem_qubits[2], problem_qubits[3]], a0)
    qc.x(problem_qubits[2])
    qc.x(problem_qubits[1])
    
    # Compute offset 1: a1 = (NOT s_2) AND (NOT s_3) AND s_4
    qc.x(problem_qubits[2])
    qc.x(problem_qubits[3])
    qc.mcx([problem_qubits[2], problem_qubits[3], problem_qubits[4]], a1)
    qc.x(problem_qubits[3])
    qc.x(problem_qubits[2])
    
    # Compute offset 2: a2 = (NOT s_3) AND (NOT s_4) AND s_5
    qc.x(problem_qubits[3])
    qc.x(problem_qubits[4])
    qc.mcx([problem_qubits[3], problem_qubits[4], problem_qubits[5]], a2)
    qc.x(problem_qubits[4])
    qc.x(problem_qubits[3])
    
    # Compute OR: result = a0 OR a1 OR a2
    # Using De Morgan: result = NOT((NOT a0) AND (NOT a1) AND (NOT a2))
    qc.x(a0)
    qc.x(a1)
    qc.x(a2)
    qc.mcx([a0, a1, a2], result)
    qc.x(result)
    qc.x(a2)
    qc.x(a1)
    qc.x(a0)
    
    # Apply phase flip
    qc.z(result)
    
    # Uncompute OR
    qc.x(a0)
    qc.x(a1)
    qc.x(a2)
    qc.x(result)
    qc.mcx([a0, a1, a2], result)
    qc.x(a2)
    qc.x(a1)
    qc.x(a0)
    
    # Uncompute offset 2
    qc.x(problem_qubits[3])
    qc.x(problem_qubits[4])
    qc.mcx([problem_qubits[3], problem_qubits[4], problem_qubits[5]], a2)
    qc.x(problem_qubits[4])
    qc.x(problem_qubits[3])
    
    # Uncompute offset 1
    qc.x(problem_qubits[2])
    qc.x(problem_qubits[3])
    qc.mcx([problem_qubits[2], problem_qubits[3], problem_qubits[4]], a1)
    qc.x(problem_qubits[3])
    qc.x(problem_qubits[2])
    
    # Uncompute offset 0
    qc.x(problem_qubits[1])
    qc.x(problem_qubits[2])
    qc.mcx([problem_qubits[1], problem_qubits[2], problem_qubits[3]], a0)
    qc.x(problem_qubits[2])
    qc.x(problem_qubits[1])
