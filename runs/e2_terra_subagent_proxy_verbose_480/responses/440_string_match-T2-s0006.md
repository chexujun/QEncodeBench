```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    a, b = ancilla_qubits[:2]
    q = problem_qubits

    # Match at offset 0: 0010?1
    for i in (0, 1, 3):
        qc.x(q[i])
    qc.mcx([q[0], q[1], q[2], q[3], q[5]], a)
    for i in (3, 1, 0):
        qc.x(q[i])

    # Match at offset 1: 0010?1
    for i in (1, 2, 4):
        qc.x(q[i])
    qc.mcx([q[1], q[2], q[3], q[4], q[6]], b)
    for i in (4, 2, 1):
        qc.x(q[i])

    # Phase flip iff a OR b.
    qc.z(a)
    qc.z(b)
    qc.cz(a, b)

    # Uncompute offset-1 match.
    for i in (1, 2, 4):
        qc.x(q[i])
    qc.mcx([q[1], q[2], q[3], q[4], q[6]], b)
    for i in (4, 2, 1):
        qc.x(q[i])

    # Uncompute offset-0 match.
    for i in (0, 1, 3):
        qc.x(q[i])
    qc.mcx([q[0], q[1], q[2], q[3], q[5]], a)
    for i in (3, 1, 0):
        qc.x(q[i])
```
