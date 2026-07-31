```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    q0, q1, q2 = problem_qubits
    qc.x(q2)
    qc.h(q2)
    qc.ccx(q0, q1, q2)
    qc.h(q2)
    qc.x(q2)
```
