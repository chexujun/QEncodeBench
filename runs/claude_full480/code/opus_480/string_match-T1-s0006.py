from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    p1 = problem_qubits[1]
    p3 = problem_qubits[3]
    qc.x(p1)
    qc.cz(p1, p3)
    qc.x(p1)
