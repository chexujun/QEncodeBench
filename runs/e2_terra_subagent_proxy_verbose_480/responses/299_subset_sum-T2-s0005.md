```python
import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    q0, q1, q2, q3 = problem_qubits

    # The only subset summing to 2 is {a[1]}, i.e. x = 0010.
    qc.x(q0)
    qc.x(q2)
    qc.x(q3)

    qc.h(q3)
    qc.mcx([q0, q1, q2], q3)
    qc.h(q3)

    qc.x(q3)
    qc.x(q2)
    qc.x(q0)
```
