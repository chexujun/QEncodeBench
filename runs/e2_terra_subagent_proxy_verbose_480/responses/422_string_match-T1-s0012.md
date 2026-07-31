```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    q0, _, q2, q3, _ = problem_qubits

    qc.x(q0)
    qc.x(q2)
    qc.h(q3)
    qc.ccx(q0, q2, q3)
    qc.h(q3)
    qc.x(q2)
    qc.x(q0)
```
