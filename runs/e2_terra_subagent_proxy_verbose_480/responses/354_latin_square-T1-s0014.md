```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    b0, b1, b2, b3 = problem_qubits
    eq = ancilla_qubits[0]

    # eq = 1 iff the first cell decodes to 0 (codes 00 or 11).
    qc.cx(b0, eq)
    qc.cx(b1, eq)
    qc.x(eq)

    # Require second cell's code to be 10: b2 = 0, b3 = 1.
    qc.x(b2)

    # CCZ(eq, b2, b3).
    qc.h(b3)
    qc.ccx(eq, b2, b3)
    qc.h(b3)

    qc.x(b2)

    # Uncompute eq.
    qc.x(eq)
    qc.cx(b1, eq)
    qc.cx(b0, eq)
```
