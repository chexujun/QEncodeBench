```python
import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    a0 = problem_qubits[0]  # cell (0,1), low bit: must be 1
    a1 = problem_qubits[1]  # cell (0,1), high bit: must be 0
    b0 = problem_qubits[2]  # cell (1,1), low bit: must be 0
    c0 = problem_qubits[4]  # cell (2,0), low bit: must be 0

    # Convert the required 0-controls to 1-controls.
    qc.x(a1)
    qc.x(b0)
    qc.x(c0)

    # Adds -1 exactly when a0=1, a1=b0=c0=0.
    qc.mcp(math.pi, [a0, a1, b0], c0)

    qc.x(c0)
    qc.x(b0)
    qc.x(a1)
```
