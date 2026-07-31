```python
import math

def build_oracle(qc, problem_qubits, ancilla_qubits):
    p = problem_qubits

    qc.x(p[0])
    qc.x(p[1])
    qc.x(p[3])
    qc.mcp(math.pi, [p[0], p[1], p[2], p[3]], p[5])
    qc.x(p[3])
    qc.x(p[1])
    qc.x(p[0])

    qc.x(p[1])
    qc.x(p[2])
    qc.x(p[4])
    qc.mcp(math.pi, [p[1], p[2], p[3], p[4]], p[6])
    qc.x(p[4])
    qc.x(p[2])
    qc.x(p[1])
```
