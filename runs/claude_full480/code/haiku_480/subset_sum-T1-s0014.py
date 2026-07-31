from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    x0 = problem_qubits[0]
    x1 = problem_qubits[1]
    x2 = problem_qubits[2]
    a = ancilla_qubits[0]
    
    # Compute: a = NOT x0 AND x1 AND NOT x2
    # This detects the unique subset {5} that sums to target T=5
    qc.x(x0)
    qc.x(x2)
    qc.mcx([x0, x1, x2], a)
    qc.x(x2)
    qc.x(x0)
    
    # Phase: Apply Z to ancilla (marks the solution state with phase -1)
    qc.z(a)
    
    # Uncompute: Reverse the compute steps
    qc.x(x0)
    qc.x(x2)
    qc.mcx([x0, x1, x2], a)
    qc.x(x2)
    qc.x(x0)
