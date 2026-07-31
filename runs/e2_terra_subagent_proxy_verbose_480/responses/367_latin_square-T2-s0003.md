```python
from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    # The three free cells must decode respectively to 1, 2, and 0.
    # Cell 0: 01; cell 1: 10; cell 2: 00 or 11.
    p = problem_qubits
    equal_zero_code = ancilla_qubits[0]
    marked = ancilla_qubits[1]

    # Compute whether cell 2's two bits are equal, i.e. it decodes to 0.
    qc.cx(p[4], equal_zero_code)
    qc.cx(p[5], equal_zero_code)
    qc.x(equal_zero_code)

    # Convert required zero literals into positive controls.
    qc.x(p[1])
    qc.x(p[2])

    # Mark iff cell 0 is 01, cell 1 is 10, and cell 2 decodes to 0.
    qc.mcx([p[0], p[1], p[2], p[3], equal_zero_code], marked)
    qc.z(marked)
    qc.mcx([p[0], p[1], p[2], p[3], equal_zero_code], marked)

    # Uncompute all temporary state.
    qc.x(p[2])
    qc.x(p[1])
    qc.x(equal_zero_code)
    qc.cx(p[5], equal_zero_code)
    qc.cx(p[4], equal_zero_code)
```
