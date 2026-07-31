```python
from qiskit import QuantumCircuit
import math

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a0, a1, b0, b1, c0, c1 = problem_qubits

    # The Latin-square constraints require:
    # cell (1,1) = 0, cell (1,2) = 2, cell (2,2) = 1.
    # Value 0 is encoded by either 00 or 11, i.e. a0 == a1.
    qc.cx(a0, a1)
    qc.x(a1)   # a1 is now 1 iff the original a0 == a1
    qc.x(b0)   # require b0 = 0
    qc.x(c1)   # require c1 = 0

    qc.mcp(math.pi, [a1, b0, b1, c0], c1)

    qc.x(c1)
    qc.x(b0)
    qc.x(a1)
    qc.cx(a0, a1)
```
