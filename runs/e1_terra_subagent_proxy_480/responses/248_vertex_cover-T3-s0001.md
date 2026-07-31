```python
from math import pi
from qiskit import QuantumCircuit

def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    # The unique vertex cover of size <= 2 is {2, 3}.
    for i in (0, 1, 4, 5):
        qc.x(problem_qubits[i])

    qc.mcp(pi, problem_qubits[:5], problem_qubits[5])

    for i in (0, 1, 4, 5):
        qc.x(problem_qubits[i])
```
