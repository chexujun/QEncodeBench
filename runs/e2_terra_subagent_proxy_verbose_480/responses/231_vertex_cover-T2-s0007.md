```python
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    q0, q1, q2, q3, q4 = problem_qubits

    # Under the size-at-most-two constraint, the unique vertex cover is
    # {2, 3}, corresponding to the bit pattern x4 x3 x2 x1 x0 = 01100.
    qc.x(q0)
    qc.x(q1)
    qc.x(q4)

    qc.h(q4)
    qc.mcx([q0, q1, q2, q3], q4)
    qc.h(q4)

    qc.x(q4)
    qc.x(q1)
    qc.x(q0)
```
