from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    x0, x1, x2 = problem_qubits[0], problem_qubits[1], problem_qubits[2]
    a2, result = ancilla_qubits[0], ancilla_qubits[1]
    
    # Compute a2 = NOT x0 OR x1
    qc.x(x1)
    qc.ccx(x0, x1, a2)
    qc.x(x1)
    qc.x(a2)
    
    # Compute result = x2 AND a2
    qc.ccx(x2, a2, result)
    
    # Apply phase
    qc.z(result)
    
    # Uncompute
    qc.ccx(x2, a2, result)
    qc.x(a2)
    qc.x(x1)
    qc.ccx(x0, x1, a2)
    qc.x(x1)
