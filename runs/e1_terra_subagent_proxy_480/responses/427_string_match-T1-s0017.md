```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    q0, q1, q2, _, q4 = problem_qubits
    qc.x(q0); qc.x(q1); qc.x(q4); qc.h(q4)
    qc.mcx([q0, q1, q2], q4)
    qc.h(q4); qc.x(q4); qc.x(q1); qc.x(q0)
```
