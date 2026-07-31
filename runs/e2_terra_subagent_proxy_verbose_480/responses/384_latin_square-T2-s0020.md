```python
import math
from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    a0, a1, b0, b1, c0, c1 = problem_qubits
    flag = ancilla_qubits[0]

    # Compute whether cell (0, 1) decodes to 0:
    # its two code bits must be equal (00 or 11).
    qc.cx(a0, flag)
    qc.cx(a1, flag)
    qc.x(flag)

    # Required codes for the other free cells are 01:
    # b0=c0=1 and b1=c1=0.
    qc.x(b1)
    qc.x(c1)

    # Apply -1 iff all validity conditions hold.
    qc.mcp(math.pi, [b0, b1, c0, c1], flag)

    qc.x(c1)
    qc.x(b1)

    # Uncompute the flag.
    qc.x(flag)
    qc.cx(a1, flag)
    qc.cx(a0, flag)
```
