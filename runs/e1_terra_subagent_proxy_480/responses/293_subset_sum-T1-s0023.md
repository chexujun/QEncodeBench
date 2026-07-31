```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    q0, q1, q2 = problem_qubits
    qc.x(q1)
    qc.x(q2)
    qc.mcp(3.141592653589793, [q1, q2], q0)
    qc.x(q1)
    qc.x(q2)
    qc.x(q0)
    qc.mcp(3.141592653589793, [q1, q2], q0)
    qc.x(q0)
```
