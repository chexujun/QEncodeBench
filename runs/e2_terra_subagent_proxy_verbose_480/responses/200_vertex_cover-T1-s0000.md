```python
from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    q0, q1, q2, q3 = problem_qubits

    # A valid cover of size <= 2 must be exactly {0, 3}.
    # Convert zero-controls on q1 and q2 into ordinary controls.
    qc.x(q1)
    qc.x(q2)

    # Controlled-Z on q3, controlled by q0, ~q1, and ~q2.
    qc.h(q3)
    qc.mcx([q0, q1, q2], q3)
    qc.h(q3)

    qc.x(q2)
    qc.x(q1)
```
