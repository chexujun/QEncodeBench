```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    a0, a1, b0, b1 = problem_qubits
    equal_b = ancilla_qubits[0]
    flag = ancilla_qubits[1]

    # Compute whether the second free cell decodes to 0: b0 == b1.
    qc.cx(b0, equal_b)
    qc.cx(b1, equal_b)
    qc.x(equal_b)

    # First free cell must be code 01, so a0=1 and a1=0.
    qc.x(a1)

    # Compute the complete validity predicate, phase it, and uncompute.
    qc.mcx([a0, a1, equal_b], flag)
    qc.z(flag)
    qc.mcx([a0, a1, equal_b], flag)

    qc.x(a1)

    # Uncompute equality ancilla.
    qc.x(equal_b)
    qc.cx(b1, equal_b)
    qc.cx(b0, equal_b)
```
