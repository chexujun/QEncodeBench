from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Pattern: "01110"
    # Check if pattern matches at any offset (0, 1, 2)
    
    a0 = ancilla_qubits[0]  # match at offset 0
    a1 = ancilla_qubits[1]  # match at offset 1
    a2 = ancilla_qubits[2]  # match at offset 2
    a_or = ancilla_qubits[3]  # OR of matches
    
    # Compute match at offset 0: s[0]=0, s[1]=1, s[2]=1, s[3]=1, s[4]=0
    qc.x(problem_qubits[0])
    qc.x(problem_qubits[4])
    qc.mcx([problem_qubits[0], problem_qubits[1], problem_qubits[2], 
            problem_qubits[3], problem_qubits[4]], a0)
    qc.x(problem_qubits[0])
    qc.x(problem_qubits[4])
    
    # Compute match at offset 1: s[1]=0, s[2]=1, s[3]=1, s[4]=1, s[5]=0
    qc.x(problem_qubits[1])
    qc.x(problem_qubits[5])
    qc.mcx([problem_qubits[1], problem_qubits[2], problem_qubits[3], 
            problem_qubits[4], problem_qubits[5]], a1)
    qc.x(problem_qubits[1])
    qc.x(problem_qubits[5])
    
    # Compute match at offset 2: s[2]=0, s[3]=1, s[4]=1, s[5]=1, s[6]=0
    qc.x(problem_qubits[2])
    qc.x(problem_qubits[6])
    qc.mcx([problem_qubits[2], problem_qubits[3], problem_qubits[4], 
            problem_qubits[5], problem_qubits[6]], a2)
    qc.x(problem_qubits[2])
    qc.x(problem_qubits[6])
    
    # Compute OR: a_or = a0 OR a1 OR a2
    # Using: a_or = NOT(AND(NOT a0, NOT a1, NOT a2))
    qc.x(a0)
    qc.x(a1)
    qc.x(a2)
    qc.mcx([a0, a1, a2], a_or)
    qc.x(a0)
    qc.x(a1)
    qc.x(a2)
    qc.x(a_or)
    
    # Apply phase to a_or
    qc.z(a_or)
    
    # Uncompute OR
    qc.x(a_or)
    qc.x(a0)
    qc.x(a1)
    qc.x(a2)
    qc.mcx([a0, a1, a2], a_or)
    qc.x(a0)
    qc.x(a1)
    qc.x(a2)
    
    # Uncompute match at offset 2
    qc.x(problem_qubits[2])
    qc.x(problem_qubits[6])
    qc.mcx([problem_qubits[2], problem_qubits[3], problem_qubits[4], 
            problem_qubits[5], problem_qubits[6]], a2)
    qc.x(problem_qubits[2])
    qc.x(problem_qubits[6])
    
    # Uncompute match at offset 1
    qc.x(problem_qubits[1])
    qc.x(problem_qubits[5])
    qc.mcx([problem_qubits[1], problem_qubits[2], problem_qubits[3], 
            problem_qubits[4], problem_qubits[5]], a1)
    qc.x(problem_qubits[1])
    qc.x(problem_qubits[5])
    
    # Uncompute match at offset 0
    qc.x(problem_qubits[0])
    qc.x(problem_qubits[4])
    qc.mcx([problem_qubits[0], problem_qubits[1], problem_qubits[2], 
            problem_qubits[3], problem_qubits[4]], a0)
    qc.x(problem_qubits[0])
    qc.x(problem_qubits[4])
