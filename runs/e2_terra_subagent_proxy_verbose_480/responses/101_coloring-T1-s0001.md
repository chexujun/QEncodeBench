```python
from qiskit import QuantumCircuit

def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    edge_flags = ancilla_qubits[:4]
    phase_ancilla = ancilla_qubits[4]
    edges = ((0, 1), (2, 3), (2, 4), (3, 4))

    # For two vertex codes a and b, decoded colors differ exactly when
    # a_low XOR a_high XOR b_low XOR b_high is 1.
    for flag, (u, v) in zip(edge_flags, edges):
        qc.cx(problem_qubits[2 * u], flag)
        qc.cx(problem_qubits[2 * u + 1], flag)
        qc.cx(problem_qubits[2 * v], flag)
        qc.cx(problem_qubits[2 * v + 1], flag)

    qc.mcx(edge_flags, phase_ancilla)
    qc.z(phase_ancilla)
    qc.mcx(edge_flags, phase_ancilla)

    for flag, (u, v) in reversed(list(zip(edge_flags, edges))):
        qc.cx(problem_qubits[2 * v + 1], flag)
        qc.cx(problem_qubits[2 * v], flag)
        qc.cx(problem_qubits[2 * u + 1], flag)
        qc.cx(problem_qubits[2 * u], flag)
```
