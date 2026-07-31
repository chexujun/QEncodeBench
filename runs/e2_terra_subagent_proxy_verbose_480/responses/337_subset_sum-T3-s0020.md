```python
import math

def build_oracle(qc, problem_qubits, ancilla_qubits):
    total = ancilla_qubits  # Six-bit register, little-endian.
    n = len(total)
    values = [14, 4, 12, 8, 7]

    def qft():
        # Treat total[n-1] as the most-significant bit.
        ordered = list(reversed(total))
        for j in range(n):
            qc.h(ordered[j])
            for k in range(j + 1, n):
                qc.cp(math.pi / (2 ** (k - j)), ordered[k], ordered[j])
        for j in range(n // 2):
            qc.swap(ordered[j], ordered[n - 1 - j])

    def inverse_qft():
        ordered = list(reversed(total))
        for j in range(n // 2):
            qc.swap(ordered[j], ordered[n - 1 - j])
        for j in range(n - 1, -1, -1):
            for k in range(n - 1, j, -1):
                qc.cp(-math.pi / (2 ** (k - j)), ordered[k], ordered[j])
            qc.h(ordered[j])

    def controlled_add(value, control, sign=1):
        for bit, qubit in enumerate(total):
            angle = sign * 2 * math.pi * value / (2 ** (n - bit))
            qc.cp(angle, control, qubit)

    qft()
    for value, control in zip(values, problem_qubits):
        controlled_add(value, control)
    inverse_qft()

    # Mark register value 12 (binary 001100).
    for bit, qubit in enumerate(total):
        if ((12 >> bit) & 1) == 0:
            qc.x(qubit)
    qc.mcp(math.pi, total[:-1], total[-1])
    for bit, qubit in enumerate(total):
        if ((12 >> bit) & 1) == 0:
            qc.x(qubit)

    qft()
    for value, control in reversed(list(zip(values, problem_qubits))):
        controlled_add(value, control, sign=-1)
    inverse_qft()
```
