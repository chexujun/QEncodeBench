```python
from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    x0, x1, x2 = problem_qubits
    work = ancilla_qubits[0]

    # Compute x0 XOR x2: exactly one selected 6-valued element.
    qc.cx(x0, work)
    qc.cx(x2, work)

    # Mark when x1 = 0 as well, so the selected sum is exactly 6.
    qc.x(x1)
    qc.cz(work, x1)
    qc.x(x1)

    # Uncompute work ancilla.
    qc.cx(x2, work)
    qc.cx(x0, work)
```
