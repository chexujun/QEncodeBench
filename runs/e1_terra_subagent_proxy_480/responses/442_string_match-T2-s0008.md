```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    q = problem_qubits
    a = ancilla_qubits[0]

    # Match at offset 0: 0101
    qc.x(q[0])
    qc.x(q[2])
    qc.mcx([q[0], q[1], q[2], q[3]], a)
    qc.z(a)
    qc.mcx([q[0], q[1], q[2], q[3]], a)
    qc.x(q[2])
    qc.x(q[0])

    # Match at offset 1: 0101
    qc.x(q[1])
    qc.x(q[3])
    qc.mcx([q[1], q[2], q[3], q[4]], a)
    qc.z(a)
    qc.mcx([q[1], q[2], q[3], q[4]], a)
    qc.x(q[3])
    qc.x(q[1])
```
