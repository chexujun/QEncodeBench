```python
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    q0, q1, q2, q3, q4 = problem_qubits

    # Convert required zeroes to positive controls.
    qc.x(q0)
    qc.x(q1)
    qc.x(q4)

    # Apply a four-qubit controlled-Z on q0, q1, q2, q4.
    qc.h(q4)
    qc.mcx([q0, q1, q2], q4)
    qc.h(q4)

    # Restore the input representation.
    qc.x(q4)
    qc.x(q1)
    qc.x(q0)
```
