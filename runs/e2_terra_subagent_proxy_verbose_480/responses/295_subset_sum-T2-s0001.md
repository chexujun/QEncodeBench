```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    q0, q1, q2, q3 = problem_qubits
    a0, a1, a2 = ancilla_qubits[:3]

    qc.x(q3)  # Target subset is x0=x1=x2=1, x3=0.

    qc.ccx(q0, q1, a0)
    qc.ccx(a0, q2, a1)
    qc.ccx(a1, q3, a2)

    qc.z(a2)

    qc.ccx(a1, q3, a2)
    qc.ccx(a0, q2, a1)
    qc.ccx(q0, q1, a0)

    qc.x(q3)
```
