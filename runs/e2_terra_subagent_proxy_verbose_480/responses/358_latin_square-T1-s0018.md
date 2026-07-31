```python
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    b00, b01, b10, b11 = problem_qubits
    equal_zero, valid = ancilla_qubits[:2]

    # First free cell decodes to 0 iff its two code bits are equal.
    qc.cx(b00, equal_zero)
    qc.cx(b01, equal_zero)
    qc.x(equal_zero)

    # Second free cell must decode to 1: b10=1, b11=0.
    qc.x(b11)

    # Mark equality(first code), b10=1, and b11=0.
    qc.mcx([equal_zero, b10, b11], valid)
    qc.z(valid)
    qc.mcx([equal_zero, b10, b11], valid)

    qc.x(b11)
    qc.x(equal_zero)
    qc.cx(b01, equal_zero)
    qc.cx(b00, equal_zero)
```
