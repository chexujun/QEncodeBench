```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    b00, b01, b10, b11 = problem_qubits
    equal_zero, marked = ancilla_qubits[:2]

    # Decode cell (0,0) as zero: its two code bits must be equal.
    qc.cx(b00, equal_zero)
    qc.cx(b01, equal_zero)
    qc.x(equal_zero)

    # Cell (0,1) must decode as one: low bit 1, high bit 0.
    qc.x(b11)
    qc.mcx([equal_zero, b10, b11], marked)
    qc.z(marked)
    qc.mcx([equal_zero, b10, b11], marked)
    qc.x(b11)

    # Uncompute the equality predicate.
    qc.x(equal_zero)
    qc.cx(b01, equal_zero)
    qc.cx(b00, equal_zero)
```
