from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Decode: c = b0 + 2*b1; values are 0,1,2,0 for codes 00,01,10,11
    # Value 0 iff b0 == b1 (XOR == 0)
    # Both free cells must decode to value 0 for valid Latin square
    
    # Compute parity for cell 0: ancilla[0] = problem_qubits[0] XOR problem_qubits[1]
    qc.cx(problem_qubits[0], ancilla_qubits[0])
    qc.cx(problem_qubits[1], ancilla_qubits[0])
    
    # Compute parity for cell 1: ancilla[1] = problem_qubits[2] XOR problem_qubits[3]
    qc.cx(problem_qubits[2], ancilla_qubits[1])
    qc.cx(problem_qubits[3], ancilla_qubits[1])
    
    # Invert parities (to check if parity == 0)
    qc.x(ancilla_qubits[0])
    qc.x(ancilla_qubits[1])
    
    # Compute AND of inverted parities into ancilla[2]
    qc.ccx(ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[2])
    
    # Apply phase -1 if both conditions are satisfied
    qc.z(ancilla_qubits[2])
    
    # Uncompute AND
    qc.ccx(ancilla_qubits[0], ancilla_qubits[1], ancilla_qubits[2])
    
    # Uninvert parities
    qc.x(ancilla_qubits[1])
    qc.x(ancilla_qubits[0])
    
    # Uncompute parity for cell 1
    qc.cx(problem_qubits[3], ancilla_qubits[1])
    qc.cx(problem_qubits[2], ancilla_qubits[1])
    
    # Uncompute parity for cell 0
    qc.cx(problem_qubits[1], ancilla_qubits[0])
    qc.cx(problem_qubits[0], ancilla_qubits[0])
