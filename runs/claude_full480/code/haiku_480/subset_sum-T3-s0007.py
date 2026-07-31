from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    ancilla = ancilla_qubits[0]
    workspace = ancilla_qubits[1:]
    
    qc.x(problem_qubits[1])
    qc.x(problem_qubits[2])
    qc.x(problem_qubits[3])
    qc.x(problem_qubits[4])
    
    qc.mcx(problem_qubits, ancilla, workspace)
    qc.z(ancilla)
    qc.mcx(problem_qubits, ancilla, workspace)
    
    qc.x(problem_qubits[4])
    qc.x(problem_qubits[3])
    qc.x(problem_qubits[2])
    qc.x(problem_qubits[1])
