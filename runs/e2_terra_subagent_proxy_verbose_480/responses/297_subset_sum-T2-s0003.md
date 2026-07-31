```python
import math
from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    acc = ancilla_qubits[:5]  # Little-endian, stores the selected-element sum.
    n = 5

    def controlled_add_power(control, start_bit, inverse=False):
        """Conditionally add/subtract 2**start_bit modulo 2**n."""
        bit_range = (
            range(start_bit, n)
            if inverse
            else range(n - 1, start_bit - 1, -1)
        )
        for bit in bit_range:
            controls = [control] + acc[start_bit:bit]
            if len(controls) == 1:
                qc.cx(control, acc[bit])
            else:
                qc.mcx(controls, acc[bit])

    # Reversibly compute 9*x0 + 3*x1 + 8*x2 + 9*x3.
    operations = [
        (problem_qubits[0], 3),  # 8
        (problem_qubits[0], 0),  # 1
        (problem_qubits[1], 1),  # 2
        (problem_qubits[1], 0),  # 1
        (problem_qubits[2], 3),  # 8
        (problem_qubits[3], 3),  # 8
        (problem_qubits[3], 0),  # 1
    ]
    for control, bit in operations:
        controlled_add_power(control, bit)

    # Mark accumulator value 9 (binary 01001).
    for bit in (1, 2, 4):
        qc.x(acc[bit])
    qc.mcp(math.pi, acc[:4], acc[4])
    for bit in (4, 2, 1):
        qc.x(acc[bit])

    # Uncompute the sum.
    for control, bit in reversed(operations):
        controlled_add_power(control, bit, inverse=True)
```
