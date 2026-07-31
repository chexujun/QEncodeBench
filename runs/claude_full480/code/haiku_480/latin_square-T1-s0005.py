from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Free cells at (1,1) and (2,2) must each have value 2 for valid Latin square
    # Value = low_bit + 2*high_bit, so value 2 requires low_bit=0 AND high_bit=1
    
    temp0 = ancilla_qubits[0]
    temp1 = ancilla_qubits[1]
    result = ancilla_qubits[2]
    
    # Compute: cell 0 has value 2 (low_bit=0 AND high_bit=1)
    qc.x(problem_qubits[0])
    qc.ccx(problem_qubits[0], problem_qubits[1], temp0)
    qc.x(problem_qubits[0])
    
    # Compute: cell 1 has value 2 (low_bit=0 AND high_bit=1)
    qc.x(problem_qubits[2])
    qc.ccx(problem_qubits[2], problem_qubits[3], temp1)
    qc.x(problem_qubits[2])
    
    # Combine: result = (cell 0 is 2) AND (cell 1 is 2)
    qc.ccx(temp0, temp1, result)
    
    # Apply phase -1 to marked states
    qc.z(result)
    
    # Uncompute to restore ancillas to |0>
    qc.ccx(temp0, temp1, result)
    
    qc.x(problem_qubits[2])
    qc.ccx(problem_qubits[2], problem_qubits[3], temp1)
    qc.x(problem_qubits[2])
    
    qc.x(problem_qubits[0])
    qc.ccx(problem_qubits[0], problem_qubits[1], temp0)
    qc.x(problem_qubits[0])
