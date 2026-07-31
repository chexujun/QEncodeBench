```python
import math

from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    q0, q1, q2, q3 = problem_qubits

    # Both free cells must decode to value 1, whose code is 01.
    qc.x(q1)
    qc.x(q3)
    qc.mcp(math.pi, [q0, q1, q2], q3)
    qc.x(q3)
    qc.x(q1)
```
