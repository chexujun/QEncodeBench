```python
import math
from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    # Since all elements except a[0] = 12 exceed the target,
    # sum == 12 iff x0 = 1 and x1 = x2 = x3 = x4 = 0.
    q0, q1, q2, q3, q4 = problem_qubits

    for qubit in (q1, q2, q3, q4):
        qc.x(qubit)

    qc.mcp(math.pi, [q1, q2, q3, q4], q0)

    for qubit in (q1, q2, q3, q4):
        qc.x(qubit)
```
