```python
import math
from qiskit import QuantumCircuit

def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    # The only vertex cover of size at most 2 is {2, 3}.
    q0, q1, q2, q3 = problem_qubits

    qc.x(q0)
    qc.x(q1)
    qc.mcp(math.pi, [q0, q1, q2], q3)
    qc.x(q1)
    qc.x(q0)
```
