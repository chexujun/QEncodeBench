from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # Pattern: "0?1?" means s_0 == 0 and s_2 == 1
    # Apply phase -1 when x_0 == 0 AND x_2 == 1
    
    # Flip x_0 so that when x_0 is originally 0, it becomes 1 and acts as a control
    qc.x(problem_qubits[0])
    
    # Apply Toffoli to compute (NOT x_0) AND x_2 into ancilla[0]
    qc.ccx(problem_qubits[0], problem_qubits[2], ancilla_qubits[0])
    
    # Apply phase flip
    qc.z(ancilla_qubits[0])
    
    # Uncompute: undo the Toffoli
    qc.ccx(problem_qubits[0], problem_qubits[2], ancilla_qubits[0])
    
    # Restore x_0 to its original value
    qc.x(problem_qubits[0])
