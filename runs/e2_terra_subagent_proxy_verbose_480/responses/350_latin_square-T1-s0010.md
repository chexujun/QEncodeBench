```python
from math import pi

def build_oracle(qc, problem_qubits, ancilla_qubits):
    q0, q1, q2, q3 = problem_qubits

    # Valid completion requires codes:
    # cell (1,2) = 01 and cell (2,1) = 10.
    qc.x(q1)
    qc.x(q2)
    qc.mcp(pi, [q0, q1, q2], q3)
    qc.x(q2)
    qc.x(q1)
```
