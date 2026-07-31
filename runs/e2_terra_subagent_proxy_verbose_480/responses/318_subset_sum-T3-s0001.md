```python
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    q0, q1, q2, q3, q4 = problem_qubits

    # With positive values [2, 15, 14, 9, 4], the sum is 9 exactly when
    # x3 = 1 and every other selection bit is 0.
    qc.x(q0)
    qc.x(q1)
    qc.x(q2)
    qc.x(q4)

    qc.h(q3)
    qc.mcx([q0, q1, q2, q4], q3)
    qc.h(q3)

    qc.x(q4)
    qc.x(q2)
    qc.x(q1)
    qc.x(q0)
```
