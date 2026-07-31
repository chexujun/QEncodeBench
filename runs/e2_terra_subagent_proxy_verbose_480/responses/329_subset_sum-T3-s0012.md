```python
import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    s = ancilla_qubits  # 5-bit little-endian accumulator
    values = [7, 2, 5, 7, 3]

    def controlled_increment(control, inverse=False):
        if inverse:
            qc.cx(control, s[0])
            for bit in range(1, 5):
                qc.mcx([control] + s[:bit], s[bit])
        else:
            for bit in range(4, 0, -1):
                qc.mcx([control] + s[:bit], s[bit])
            qc.cx(control, s[0])

    # Compute the selected-element sum modulo 32.
    for q, value in zip(problem_qubits, values):
        for _ in range(value):
            controlled_increment(q)

    # Mark accumulator value 7 (binary 00111).
    qc.x(s[3])
    qc.x(s[4])
    qc.mcp(math.pi, [s[0], s[1], s[3], s[4]], s[2])
    qc.x(s[4])
    qc.x(s[3])

    # Uncompute the accumulator.
    for q, value in reversed(list(zip(problem_qubits, values))):
        for _ in range(value):
            controlled_increment(q, inverse=True)
```
