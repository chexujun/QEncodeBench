```python
import math
from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    a0, a1, b0, b1 = problem_qubits
    flag = ancilla_qubits[0]

    # The first free cell must decode to 0: a0 == a1.
    qc.cx(a0, flag)
    qc.cx(a1, flag)
    qc.x(flag)

    # The second free cell must decode to 1: b0 == 1 and b1 == 0.
    qc.x(b1)
    qc.mcp(math.pi, [b0, b1], flag)
    qc.x(b1)

    qc.x(flag)
    qc.cx(a1, flag)
    qc.cx(a0, flag)
```
