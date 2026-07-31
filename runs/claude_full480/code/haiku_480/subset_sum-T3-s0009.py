from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    flag = ancilla_qubits[0]
    
    # For a = [3, 14, 3, 13, 3] and target T = 6:
    # Since 14 > 6 and 13 > 6, we must have x[1] = 0 and x[3] = 0.
    # The sum equals 6 iff x[1] = 0, x[3] = 0, and x[0] + x[2] + x[4] = 2.
    # Valid states (as binary x[4]x[3]x[2]x[1]x[0]):
    # - 00101 (x[0]=1, x[2]=1, x[4]=0): sum = 3+3+0 = 6 ✓
    # - 10001 (x[0]=1, x[2]=0, x[4]=1): sum = 3+0+3 = 6 ✓
    # - 10100 (x[0]=0, x[2]=1, x[4]=1): sum = 0+3+3 = 6 ✓
    
    # Compute: For each valid state, flip problem qubits to make all = 1,
    # then apply mcx to set flag = 1
    
    # State 00101: flip x[1], x[3], x[4] to align
    qc.x(problem_qubits[1])
    qc.x(problem_qubits[3])
    qc.x(problem_qubits[4])
    qc.mcx([problem_qubits[0], problem_qubits[1], problem_qubits[2], problem_qubits[3], problem_qubits[4]], flag)
    qc.x(problem_qubits[1])
    qc.x(problem_qubits[3])
    qc.x(problem_qubits[4])
    
    # State 10001: flip x[1], x[2], x[3]
    qc.x(problem_qubits[1])
    qc.x(problem_qubits[2])
    qc.x(problem_qubits[3])
    qc.mcx([problem_qubits[0], problem_qubits[1], problem_qubits[2], problem_qubits[3], problem_qubits[4]], flag)
    qc.x(problem_qubits[1])
    qc.x(problem_qubits[2])
    qc.x(problem_qubits[3])
    
    # State 10100: flip x[0], x[1], x[3]
    qc.x(problem_qubits[0])
    qc.x(problem_qubits[1])
    qc.x(problem_qubits[3])
    qc.mcx([problem_qubits[0], problem_qubits[1], problem_qubits[2], problem_qubits[3], problem_qubits[4]], flag)
    qc.x(problem_qubits[0])
    qc.x(problem_qubits[1])
    qc.x(problem_qubits[3])
    
    # Apply phase: flag is 1 iff we are in a valid state
    qc.z(flag)
    
    # Uncompute: reverse all steps to return flag to |0⟩
    qc.x(problem_qubits[0])
    qc.x(problem_qubits[1])
    qc.x(problem_qubits[3])
    qc.mcx([problem_qubits[0], problem_qubits[1], problem_qubits[2], problem_qubits[3], problem_qubits[4]], flag)
    qc.x(problem_qubits[0])
    qc.x(problem_qubits[1])
    qc.x(problem_qubits[3])
    
    qc.x(problem_qubits[1])
    qc.x(problem_qubits[2])
    qc.x(problem_qubits[3])
    qc.mcx([problem_qubits[0], problem_qubits[1], problem_qubits[2], problem_qubits[3], problem_qubits[4]], flag)
    qc.x(problem_qubits[1])
    qc.x(problem_qubits[2])
    qc.x(problem_qubits[3])
    
    qc.x(problem_qubits[1])
    qc.x(problem_qubits[3])
    qc.x(problem_qubits[4])
    qc.mcx([problem_qubits[0], problem_qubits[1], problem_qubits[2], problem_qubits[3], problem_qubits[4]], flag)
    qc.x(problem_qubits[1])
    qc.x(problem_qubits[3])
    qc.x(problem_qubits[4])
