```python
import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    # The Latin-square constraints require decoded values (1, 1, 2),
    # corresponding uniquely to codes 01, 01, 10.
    zero_bits = [
        problem_qubits[1],
        problem_qubits[3],
        problem_qubits[4],
    ]

    for qubit in zero_bits:
        qc.x(qubit)

    qc.mcp(
        math.pi,
        problem_qubits[:5],
        problem_qubits[5],
    )

    for qubit in reversed(zero_bits):
        qc.x(qubit)
```
