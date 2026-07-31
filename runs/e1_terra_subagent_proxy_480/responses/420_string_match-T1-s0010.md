```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    q0, q1, _, q3 = problem_qubits
    qc.x(q0)
    qc.h(q3)
    qc.ccx(q0, q1, q3)
    qc.h(q3)
    qc.x(q0)
```
