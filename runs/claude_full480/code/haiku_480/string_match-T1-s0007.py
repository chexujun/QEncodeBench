from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a = ancilla_qubits[0]
    # Compute: copy problem_qubits[1] to ancilla
    qc.cx(problem_qubits[1], a)
    # Phase: apply Z to mark states where problem_qubits[1] = 1
    qc.z(a)
    # Uncompute: restore ancilla to |0>
    qc.cx(problem_qubits[1], a)
