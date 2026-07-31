```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    q0, q1, q2 = problem_qubits

    qc.x(q0)
    qc.x(q1)
    qc.h(q2)
    qc.mcx([q0, q1], q2)
    qc.h(q2)
    qc.x(q1)
    qc.x(q0)
```
