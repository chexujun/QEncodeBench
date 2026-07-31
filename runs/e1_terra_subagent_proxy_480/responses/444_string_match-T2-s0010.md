```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    q = problem_qubits
    qc.x(q[0]); qc.x(q[1]); qc.x(q[5]); qc.h(q[5]); qc.mcx([q[0], q[1], q[2]], q[5]); qc.h(q[5]); qc.x(q[5]); qc.x(q[1]); qc.x(q[0])
    qc.x(q[1]); qc.x(q[2]); qc.x(q[6]); qc.h(q[6]); qc.mcx([q[1], q[2], q[3]], q[6]); qc.h(q[6]); qc.x(q[6]); qc.x(q[2]); qc.x(q[1])
```
