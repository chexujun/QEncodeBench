```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    a0, a1, b0, b1, c0, c1 = problem_qubits
    eq = ancilla_qubits[0]

    # Compute whether the third free-cell code decodes to 0:
    # its two code bits must be equal (00 or 11).
    qc.cx(c0, eq)
    qc.cx(c1, eq)

    # Convert required zero-valued literals into positive controls.
    qc.x(a1)
    qc.x(b0)
    qc.x(eq)

    # Apply a phase iff:
    # A = 01, B = 10, and C's bits are equal.
    qc.h(a0)
    qc.mcx([a1, b0, b1, eq], a0)
    qc.h(a0)

    # Uncompute.
    qc.x(eq)
    qc.x(b0)
    qc.x(a1)
    qc.cx(c1, eq)
    qc.cx(c0, eq)
```
