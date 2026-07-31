```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    q0, q1, _, _, q4, q5 = problem_qubits
    a0, a1 = ancilla_qubits

    qc.ccx(q0, q1, a0)
    qc.x(q4)
    qc.ccx(q4, q5, a1)

    qc.cz(a0, a1)

    qc.ccx(q4, q5, a1)
    qc.x(q4)
    qc.ccx(q0, q1, a0)
```
