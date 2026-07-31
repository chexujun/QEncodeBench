```python
import math
def build_oracle(qc, problem_qubits, ancilla_qubits):
    q = problem_qubits
    qc.x(q[3]); qc.mcp(math.pi, [q[0], q[1], q[3]], q[4]); qc.x(q[3])
    qc.x(q[4]); qc.mcp(math.pi, [q[1], q[2], q[4]], q[5]); qc.x(q[4])
    qc.x(q[5]); qc.mcp(math.pi, [q[2], q[3], q[5]], q[6]); qc.x(q[5])
```
