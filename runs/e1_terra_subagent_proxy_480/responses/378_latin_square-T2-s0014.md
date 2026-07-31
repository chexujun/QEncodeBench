```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    from math import pi

    for x_bits in ((0, 0), (1, 1)):
        for y_bits in ((0, 0), (1, 1)):
            bits = (*x_bits, *y_bits, 1, 0)
            flipped = [q for q, bit in zip(problem_qubits, bits) if bit == 0]
            for q in flipped:
                qc.x(q)
            qc.mcp(pi, problem_qubits[:-1], problem_qubits[-1])
            for q in reversed(flipped):
                qc.x(q)
```
