```python
import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x0, x1, x2, x3, x4 = problem_qubits
    parity = ancilla_qubits[0]

    # For a vertex cover of size at most two, x3 must be selected.
    # The remaining constraints reduce to:
    #   not x0, not x1, and exactly one of x2 and x4.
    qc.cx(x2, parity)
    qc.cx(x4, parity)

    qc.x(x0)
    qc.x(x1)
    qc.mcp(math.pi, [x0, x1, x3], parity)
    qc.x(x1)
    qc.x(x0)

    qc.cx(x4, parity)
    qc.cx(x2, parity)
```
