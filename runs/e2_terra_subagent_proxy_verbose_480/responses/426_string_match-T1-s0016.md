```python
import math
from qiskit import QuantumCircuit

def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    q0, q1, q2, q3, q4 = problem_qubits

    qc.x(q0)
    qc.x(q3)
    qc.mcp(math.pi, [q0, q1, q2, q3], q4)
    qc.x(q3)
    qc.x(q0)
```
