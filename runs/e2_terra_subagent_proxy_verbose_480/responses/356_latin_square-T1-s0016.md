```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    q0, q1, q2, _q3 = problem_qubits

    # Mark exactly: first free cell = 1 (01), second free cell = 0
    # (codes 00 or 11, equivalently its low bit is 0).
    qc.x(q1)
    qc.x(q2)
    qc.h(q2)
    qc.ccx(q0, q1, q2)
    qc.h(q2)
    qc.x(q2)
    qc.x(q1)
```
