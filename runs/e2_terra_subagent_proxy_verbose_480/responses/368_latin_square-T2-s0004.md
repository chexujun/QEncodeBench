```python
from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    a0, a1, b0, b1, c0, c1 = problem_qubits
    equal_a = ancilla_qubits[0]
    valid = ancilla_qubits[1]

    # The middle cell is value 0 iff its two code bits are equal.
    qc.cx(a0, equal_a)
    qc.cx(a1, equal_a)
    qc.x(equal_a)

    # Required values for the other cells: b = 2 (10), c = 1 (01).
    qc.x(b0)
    qc.x(c1)

    controls = [equal_a, b0, b1, c0, c1]
    qc.mcx(controls, valid)
    qc.z(valid)
    qc.mcx(controls, valid)

    qc.x(c1)
    qc.x(b0)

    qc.x(equal_a)
    qc.cx(a1, equal_a)
    qc.cx(a0, equal_a)
```
