```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    a_low, a_high, b_low, b_high = problem_qubits
    equal_b = ancilla_qubits[0]
    flag = ancilla_qubits[1]

    # Compute whether the second free cell decodes to 0:
    # its two code bits must be equal (00 or 11).
    qc.cx(b_low, equal_b)
    qc.cx(b_high, equal_b)
    qc.x(equal_b)

    # The first free cell must be code 10 (value 2), and the
    # second must decode to 0.
    qc.x(a_low)
    qc.mcx([a_low, a_high, equal_b], flag)

    qc.z(flag)

    qc.mcx([a_low, a_high, equal_b], flag)
    qc.x(a_low)

    # Uncompute equality flag.
    qc.x(equal_b)
    qc.cx(b_high, equal_b)
    qc.cx(b_low, equal_b)
```
