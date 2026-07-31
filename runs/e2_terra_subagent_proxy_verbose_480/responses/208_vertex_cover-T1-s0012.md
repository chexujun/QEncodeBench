```python
import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x0, x1, x2, x3 = problem_qubits
    parity = ancilla_qubits[0]

    # Valid covers of size <= 2 require:
    # x1 = 1, x2 = 0, and exactly one of x0, x3 is 1.
    qc.cx(x0, parity)
    qc.cx(x3, parity)

    qc.x(x2)
    qc.mcp(math.pi, [x1, x2, parity])
    qc.x(x2)

    qc.cx(x3, parity)
    qc.cx(x0, parity)
```
