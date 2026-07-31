```python
import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    acc = ancilla_qubits  # Little-endian 5-bit subset-sum accumulator.

    def add_power_of_two(control: int, bit: int) -> None:
        """Conditionally add 2**bit to acc modulo 2**len(acc)."""
        for target_bit in range(len(acc) - 1, bit, -1):
            qc.mcx([control] + acc[bit:target_bit], acc[target_bit])
        qc.cx(control, acc[bit])

    operations = []
    for control, value in zip(problem_qubits, (8, 8, 10, 3)):
        for bit in range(len(acc)):
            if (value >> bit) & 1:
                add_power_of_two(control, bit)
                operations.append((control, bit))

    # Mark accumulator value 18 = 10010 (little-endian).
    for bit in (0, 2, 3):
        qc.x(acc[bit])
    qc.mcp(math.pi, acc[:4], acc[4])
    for bit in (3, 2, 0):
        qc.x(acc[bit])

    # Uncompute the accumulator.
    for control, bit in reversed(operations):
        qc.cx(control, acc[bit])
        for target_bit in range(bit + 1, len(acc)):
            qc.mcx([control] + acc[bit:target_bit], acc[target_bit])
```
