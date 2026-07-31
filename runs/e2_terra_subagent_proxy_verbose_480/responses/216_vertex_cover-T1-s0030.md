```python
import math
from qiskit import QuantumCircuit

def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    q0, q1, q2, q3 = problem_qubits

    # The sole vertex cover of size <= 2 is {0, 1}: x = 0011.
    qc.x(q2)
    qc.x(q3)
    qc.mcp(math.pi, [q0, q1, q2], q3)
    qc.x(q3)
    qc.x(q2)
```
