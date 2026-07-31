```python
import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    q = problem_qubits

    # Match at offset 0: 0011?
    qc.x(q[0])
    qc.x(q[1])
    qc.mcp(math.pi, [q[0], q[1], q[2]], q[3])
    qc.x(q[1])
    qc.x(q[0])

    # Match at offset 1: ?0011
    qc.x(q[1])
    qc.x(q[2])
    qc.mcp(math.pi, [q[1], q[2], q[3]], q[4])
    qc.x(q[2])
    qc.x(q[1])
```
