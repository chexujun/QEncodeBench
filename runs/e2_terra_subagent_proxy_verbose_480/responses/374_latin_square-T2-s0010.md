```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    q = problem_qubits

    # Required decoded values: (1, 2, 1), encoded as 01, 10, 01.
    qc.x(q[1])
    qc.x(q[2])
    qc.x(q[5])

    qc.h(q[4])
    qc.mcx([q[0], q[1], q[2], q[3], q[5]], q[4])
    qc.h(q[4])

    qc.x(q[5])
    qc.x(q[2])
    qc.x(q[1])
```
