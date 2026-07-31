```python
from qiskit import QuantumCircuit
import math


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    acc = ancilla_qubits  # Little-endian 5-bit accumulator.

    def add_power(control, shift):
        """Conditionally add 2**shift to acc modulo 32."""
        for bit in range(4, shift, -1):
            qc.mcx([control] + acc[shift:bit], acc[bit])
        qc.cx(control, acc[shift])

    def subtract_power(control, shift):
        """Inverse of add_power."""
        qc.cx(control, acc[shift])
        for bit in range(shift + 1, 5):
            qc.mcx([control] + acc[shift:bit], acc[bit])

    # Compute 4*x0 + 10*x1 + 5*x2 + 6*x3 into acc.
    additions = [
        (problem_qubits[0], 2),
        (problem_qubits[1], 3),
        (problem_qubits[1], 1),
        (problem_qubits[2], 2),
        (problem_qubits[2], 0),
        (problem_qubits[3], 2),
        (problem_qubits[3], 1),
    ]
    for control, shift in additions:
        add_power(control, shift)

    # Mark accumulator value 20 = 10100.
    for bit in (0, 1, 3):
        qc.x(acc[bit])
    qc.mcp(math.pi, acc[:4], acc[4])
    for bit in (3, 1, 0):
        qc.x(acc[bit])

    # Uncompute the accumulator.
    for control, shift in reversed(additions):
        subtract_power(control, shift)
```
