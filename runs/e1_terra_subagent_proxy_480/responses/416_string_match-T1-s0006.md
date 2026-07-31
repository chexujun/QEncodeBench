```python
from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    qc.x(problem_qubits[1])
    qc.cz(problem_qubits[1], problem_qubits[3])
    qc.x(problem_qubits[1])
```
