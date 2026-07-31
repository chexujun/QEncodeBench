```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    q = problem_qubits
    target = ancilla_qubits[0]

    qc.cx(q[2], q[3])
    qc.x(q[3])
    qc.cx(q[4], q[5])
    qc.x(q[5])

    qc.x(q[0])
    qc.x(q[7])
    qc.mcx([q[0], q[1], q[3], q[5], q[6], q[7]], target)
    qc.x(q[7])
    qc.x(q[0])

    qc.x(q[5])
    qc.cx(q[4], q[5])
    qc.x(q[3])
    qc.cx(q[2], q[3])
```
