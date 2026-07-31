```python
import math
from qiskit import QuantumCircuit

def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    q0, q1, q2 = problem_qubits

    # The only solution is x = 100 (little-endian bits: x2=1, x0=x1=0).
    qc.x(q0)
    qc.x(q1)
    qc.mcp(math.pi, [q0, q1], q2)
    qc.x(q1)
    qc.x(q0)
```
