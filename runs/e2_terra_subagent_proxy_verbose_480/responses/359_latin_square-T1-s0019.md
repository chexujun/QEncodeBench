```python
import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    q0, q1, q2, q3 = problem_qubits

    # Valid completion requires both free cells to decode to value 2:
    # (b0, b1) = (0, 1).
    qc.x(q0)
    qc.x(q2)

    qc.h(q3)
    qc.mcx([q0, q1, q2], q3)
    qc.h(q3)

    qc.x(q2)
    qc.x(q0)
```
