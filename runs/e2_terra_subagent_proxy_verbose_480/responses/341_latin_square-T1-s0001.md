```python
from qiskit import QuantumCircuit

def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    a0, a1, b0, b1 = problem_qubits
    equal_a = ancilla_qubits[0]
    flag = ancilla_qubits[1]

    # First free-cell value is 0 iff its two code bits are equal.
    qc.cx(a0, equal_a)
    qc.cx(a1, equal_a)

    # Flag: (equal_a == 0) AND (b0 == 1) AND (b1 == 0).
    qc.x(equal_a)
    qc.x(b1)
    qc.mcx([equal_a, b0, b1], flag)
    qc.z(flag)
    qc.mcx([equal_a, b0, b1], flag)
    qc.x(b1)
    qc.x(equal_a)

    # Uncompute equality.
    qc.cx(a1, equal_a)
    qc.cx(a0, equal_a)
```
