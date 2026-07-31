from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a0 = ancilla_qubits[0]
    a1 = ancilla_qubits[1]
    a2 = ancilla_qubits[2]
    
    # Compute match at offset 0: s_0=1, s_1=0, s_2=1, s_3=0, s_4=0, s_5=0
    qc.x(problem_qubits[1])
    qc.x(problem_qubits[3])
    qc.x(problem_qubits[4])
    qc.x(problem_qubits[5])
    qc.mcx([problem_qubits[0], problem_qubits[1], problem_qubits[2], 
            problem_qubits[3], problem_qubits[4], problem_qubits[5]], a0)
    qc.x(problem_qubits[1])
    qc.x(problem_qubits[3])
    qc.x(problem_qubits[4])
    qc.x(problem_qubits[5])
    
    # Compute match at offset 1: s_1=1, s_2=0, s_3=1, s_4=0, s_5=0, s_6=0
    qc.x(problem_qubits[2])
    qc.x(problem_qubits[4])
    qc.x(problem_qubits[5])
    qc.x(problem_qubits[6])
    qc.mcx([problem_qubits[1], problem_qubits[2], problem_qubits[3], 
            problem_qubits[4], problem_qubits[5], problem_qubits[6]], a1)
    qc.x(problem_qubits[2])
    qc.x(problem_qubits[4])
    qc.x(problem_qubits[5])
    qc.x(problem_qubits[6])
    
    # Compute OR of a0 and a1 into a2
    qc.cx(a0, a2)
    qc.cx(a1, a2)
    qc.ccx(a0, a1, a2)
    
    # Apply phase
    qc.z(a2)
    
    # Uncompute OR
    qc.ccx(a0, a1, a2)
    qc.cx(a1, a2)
    qc.cx(a0, a2)
    
    # Uncompute match at offset 1
    qc.x(problem_qubits[2])
    qc.x(problem_qubits[4])
    qc.x(problem_qubits[5])
    qc.x(problem_qubits[6])
    qc.mcx([problem_qubits[1], problem_qubits[2], problem_qubits[3], 
            problem_qubits[4], problem_qubits[5], problem_qubits[6]], a1)
    qc.x(problem_qubits[2])
    qc.x(problem_qubits[4])
    qc.x(problem_qubits[5])
    qc.x(problem_qubits[6])
    
    # Uncompute match at offset 0
    qc.x(problem_qubits[1])
    qc.x(problem_qubits[3])
    qc.x(problem_qubits[4])
    qc.x(problem_qubits[5])
    qc.mcx([problem_qubits[0], problem_qubits[1], problem_qubits[2], 
            problem_qubits[3], problem_qubits[4], problem_qubits[5]], a0)
    qc.x(problem_qubits[1])
    qc.x(problem_qubits[3])
    qc.x(problem_qubits[4])
    qc.x(problem_qubits[5])
