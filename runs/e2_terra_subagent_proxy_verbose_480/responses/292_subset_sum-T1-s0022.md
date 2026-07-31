```python
import math
from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    x0, x1, x2 = problem_qubits

    # 4*x0 + 2*x1 + 5*x2 = 7 iff x0 = 0, x1 = 1, x2 = 1.
    qc.x(x0)
    qc.mcp(math.pi, [x0, x1, x2])
    qc.x(x0)
```
