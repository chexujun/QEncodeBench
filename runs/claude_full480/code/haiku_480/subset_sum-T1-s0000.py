from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x0, x1, x2 = problem_qubits[0], problem_qubits[1], problem_qubits[2]
    a0, a1 = ancilla_qubits[0], ancilla_qubits[1]
    
    qc.cx(x1, a0)
    qc.cx(x2, a0)
    qc.ccx(x0, a0, a1)
    qc.z(a1)
    qc.ccx(x0, a0, a1)
    qc.cx(x2, a0)
    qc.cx(x1, a0)
