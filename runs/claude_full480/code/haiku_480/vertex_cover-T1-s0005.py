from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a = ancilla_qubits[0]
    
    # The only vertex cover of size ≤ 2 is {2, 3}
    # This corresponds to the state |0011> where:
    # problem_qubits[0] = 0, problem_qubits[1] = 0,
    # problem_qubits[2] = 1, problem_qubits[3] = 1
    
    # Flip qubits 0 and 1 so we're detecting |1111>
    qc.x(problem_qubits[0])
    qc.x(problem_qubits[1])
    
    # Compute: set ancilla to 1 iff all 4 problem qubits are 1
    qc.mcx(problem_qubits, a)
    
    # Apply phase -1
    qc.z(a)
    
    # Uncompute: reset ancilla to 0
    qc.mcx(problem_qubits, a)
    
    # Unflip qubits 0 and 1
    qc.x(problem_qubits[0])
    qc.x(problem_qubits[1])
