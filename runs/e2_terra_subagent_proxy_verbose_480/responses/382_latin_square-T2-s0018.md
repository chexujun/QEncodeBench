```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    q0, q1, q2, q3, q4, q5 = problem_qubits
    equal_zero = ancilla_qubits[0]
    valid = ancilla_qubits[1]

    # The middle free cell decodes to 0 iff its two code bits are equal.
    qc.cx(q2, equal_zero)
    qc.cx(q3, equal_zero)
    qc.x(equal_zero)

    # Required decoded values are: cell 0 = 1, cell 1 = 0, cell 2 = 2.
    qc.x(q1)
    qc.x(q4)
    qc.mcx([q0, q1, equal_zero, q4, q5], valid)
    qc.z(valid)
    qc.mcx([q0, q1, equal_zero, q4, q5], valid)
    qc.x(q4)
    qc.x(q1)

    # Uncompute equality predicate.
    qc.x(equal_zero)
    qc.cx(q3, equal_zero)
    qc.cx(q2, equal_zero)
```
