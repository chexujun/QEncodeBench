```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    q0, q1, q2, q3, q4 = problem_qubits
    a, b = ancilla_qubits[:2]

    # Compute match at offset 0: 0100
    qc.x(q0)
    qc.x(q2)
    qc.x(q3)
    qc.mcx([q0, q1, q2, q3], a)
    qc.x(q3)
    qc.x(q2)
    qc.x(q0)

    # Compute match at offset 1: 0100
    qc.x(q1)
    qc.x(q3)
    qc.x(q4)
    qc.mcx([q1, q2, q3, q4], b)
    qc.x(q4)
    qc.x(q3)
    qc.x(q1)

    # Apply phase iff either match flag is set.
    qc.z(a)
    qc.z(b)
    qc.cz(a, b)

    # Uncompute offset 1 match.
    qc.x(q1)
    qc.x(q3)
    qc.x(q4)
    qc.mcx([q1, q2, q3, q4], b)
    qc.x(q4)
    qc.x(q3)
    qc.x(q1)

    # Uncompute offset 0 match.
    qc.x(q0)
    qc.x(q2)
    qc.x(q3)
    qc.mcx([q0, q1, q2, q3], a)
    qc.x(q3)
    qc.x(q2)
    qc.x(q0)
```
