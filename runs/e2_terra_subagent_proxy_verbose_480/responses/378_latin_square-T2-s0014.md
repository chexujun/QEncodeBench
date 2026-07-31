```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    b00, b01, b10, b11, b20, b21 = problem_qubits
    eq0, eq1, val1, marked = ancilla_qubits[:4]

    # Cell 0 decodes to 0 iff its two code bits are equal.
    qc.x(eq0)
    qc.cx(b00, eq0)
    qc.cx(b01, eq0)

    # Cell 1 decodes to 0 iff its two code bits are equal.
    qc.x(eq1)
    qc.cx(b10, eq1)
    qc.cx(b11, eq1)

    # Cell 2 decodes to 1 iff its code is 01.
    qc.x(b21)
    qc.ccx(b20, b21, val1)
    qc.x(b21)

    # Mark exactly when all three forced cell-value constraints hold.
    qc.mcx([eq0, eq1, val1], marked)
    qc.z(marked)
    qc.mcx([eq0, eq1, val1], marked)

    # Uncompute all work qubits.
    qc.x(b21)
    qc.ccx(b20, b21, val1)
    qc.x(b21)

    qc.cx(b11, eq1)
    qc.cx(b10, eq1)
    qc.x(eq1)

    qc.cx(b01, eq0)
    qc.cx(b00, eq0)
    qc.x(eq0)
```
