```python
from math import pi
from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    # The unique valid cover of size at most 3 is {0, 3, 5}.
    for index in (1, 2, 4):
        qc.x(problem_qubits[index])

    qc.mcp(pi, problem_qubits[:5], problem_qubits[5])

    for index in (1, 2, 4):
        qc.x(problem_qubits[index])
```
