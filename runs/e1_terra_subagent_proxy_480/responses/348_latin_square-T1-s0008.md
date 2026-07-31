```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    q0, q1, q2, q3 = problem_qubits[:4]
    qc.x(q1)
    qc.x(q3)
    qc.mcp(3.141592653589793, [q0, q1, q2], q3)
    qc.x(q3)
    qc.x(q1)
```
