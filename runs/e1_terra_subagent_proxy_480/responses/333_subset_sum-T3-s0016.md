```python
def build_oracle(qc, problem_qubits, ancilla_qubits) -> None:
    q0, q1, q2, q3, q4 = problem_qubits

    qc.x(q1)
    qc.x(q3)
    qc.h(q4)
    qc.mcx([q0, q1, q2, q3], q4)
    qc.h(q4)
    qc.x(q3)
    qc.x(q1)

    qc.x(q0)
    qc.x(q1)
    qc.h(q4)
    qc.mcx([q0, q1, q2, q3], q4)
    qc.h(q4)
    qc.x(q1)
    qc.x(q0)
```
