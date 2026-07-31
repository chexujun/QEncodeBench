```python
from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    q0, q1, q2, q3, q4, q5 = problem_qubits
    eq_zero = ancilla_qubits[0]

    # Compute whether the second free-cell code is 00 or 11.
    qc.cx(q2, eq_zero)
    qc.cx(q3, eq_zero)
    qc.x(eq_zero)

    # Mark: cell 0 = 2, cell 1 = 0, cell 2 = 1.
    # Convert the required zero-valued bits q0 and q5 into positive controls.
    qc.x(q0)
    qc.x(q5)
    qc.h(q0)
    qc.mcx([q1, eq_zero, q4, q5], q0)
    qc.h(q0)
    qc.x(q5)
    qc.x(q0)

    # Uncompute the equality flag.
    qc.x(eq_zero)
    qc.cx(q3, eq_zero)
    qc.cx(q2, eq_zero)
```
