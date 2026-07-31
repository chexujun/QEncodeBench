```python
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    x0, x1, x2, x3 = problem_qubits
    equal_flag, predicate_flag = ancilla_qubits[:2]

    # equal_flag = 1 iff the second cell's code is 00 or 11,
    # which are precisely the two encodings of value 0.
    qc.x(equal_flag)
    qc.cx(x2, equal_flag)
    qc.cx(x3, equal_flag)

    # The first cell has value 2 exactly when its code is 10:
    # x0 = 0 and x1 = 1.
    qc.x(x0)
    qc.mcx([x0, x1, equal_flag], predicate_flag)
    qc.z(predicate_flag)
    qc.mcx([x0, x1, equal_flag], predicate_flag)
    qc.x(x0)

    # Uncompute the decoded-value equality predicate.
    qc.cx(x3, equal_flag)
    qc.cx(x2, equal_flag)
    qc.x(equal_flag)
```
