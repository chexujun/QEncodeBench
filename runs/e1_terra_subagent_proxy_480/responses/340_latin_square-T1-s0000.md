```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    q = problem_qubits
    qc.x(q[0])
    qc.x(q[1])
    qc.x(q[2])
    qc.mcp(3.141592653589793, [q[0], q[1], q[2]], q[3])
    qc.x(q[2])
    qc.x(q[1])
    qc.x(q[0])
```
