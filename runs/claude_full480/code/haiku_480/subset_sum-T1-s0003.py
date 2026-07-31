from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    x0, x1, x2 = problem_qubits[0], problem_qubits[1], problem_qubits[2]
    anc = ancilla_qubits[0]
    
    # Apply phase -1 if x0=1, x1=0, x2=1 (which sums to 8)
    # Use compute-phase-uncompute pattern
    qc.x(x1)
    qc.mcx([x0, x1, x2], anc)
    qc.z(anc)
    qc.mcx([x0, x1, x2], anc)
    qc.x(x1)
