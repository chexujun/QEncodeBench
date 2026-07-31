```python
import math

from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    x0, x1, x2, x3 = problem_qubits
    parity = ancilla_qubits[0]

    # For this graph with k=2, the predicate simplifies to:
    # x1 AND (NOT x3) AND (x0 XOR x2).
    qc.cx(x0, parity)
    qc.cx(x2, parity)

    qc.x(x3)
    qc.mcp(math.pi, [parity, x1], x3)
    qc.x(x3)

    qc.cx(x2, parity)
    qc.cx(x0, parity)
```
