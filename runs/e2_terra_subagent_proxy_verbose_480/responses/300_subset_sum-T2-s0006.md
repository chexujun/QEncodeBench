```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    q0, q1, q2, q3 = problem_qubits

    qc.x(q1)
    qc.x(q2)
    qc.x(q3)

    qc.h(q0)
    qc.mcx([q1, q2, q3], q0)
    qc.h(q0)

    qc.x(q3)
    qc.x(q2)
    qc.x(q1)
```
