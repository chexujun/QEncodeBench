from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    result = ancilla_qubits[0]
    and_temp1 = ancilla_qubits[1]
    and_temp2 = ancilla_qubits[2]
    or_temp = ancilla_qubits[3]
    
    offsets_bits = [
        [0, 1, 2],
        [1, 2, 3],
        [2, 3, 4],
        [3, 4, 5],
        [4, 5, 6],
    ]
    
    # Forward pass: compute AND and OR for each offset
    for bits in offsets_bits:
        # Compute AND of 3 bits into and_temp2
        qc.ccx(problem_qubits[bits[0]], problem_qubits[bits[1]], and_temp1)
        qc.ccx(and_temp1, problem_qubits[bits[2]], and_temp2)
        
        # Compute OR: result = result OR and_temp2
        qc.ccx(result, and_temp2, or_temp)
        qc.cx(and_temp2, result)
        qc.cx(or_temp, result)
    
    # Apply phase -1 to solutions
    qc.z(result)
    
    # Backward pass: uncompute in reverse order
    for bits in reversed(offsets_bits):
        # Recompute AND of 3 bits
        qc.ccx(problem_qubits[bits[0]], problem_qubits[bits[1]], and_temp1)
        qc.ccx(and_temp1, problem_qubits[bits[2]], and_temp2)
        
        # Uncompute OR
        qc.cx(or_temp, result)
        qc.cx(and_temp2, result)
        qc.ccx(result, and_temp2, or_temp)
        
        # Uncompute AND
        qc.ccx(and_temp1, problem_qubits[bits[2]], and_temp2)
        qc.ccx(problem_qubits[bits[0]], problem_qubits[bits[1]], and_temp1)
