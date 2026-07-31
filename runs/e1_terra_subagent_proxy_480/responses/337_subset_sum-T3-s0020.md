```python
def build_oracle(qc, problem_qubits, ancilla_qubits) -> None:
    q = problem_qubits

    for i in (0, 1, 3, 4):
        qc.x(q[i])
    qc.h(q[4])
    qc.mcx(q[:4], q[4])
    qc.h(q[4])
    for i in (0, 1, 3, 4):
        qc.x(q[i])

    for i in (0, 2, 4):
        qc.x(q[i])
    qc.h(q[4])
    qc.mcx(q[:4], q[4])
    qc.h(q[4])
    for i in (0, 2, 4):
        qc.x(q[i])
```
