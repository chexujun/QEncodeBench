```python
from math import pi

def build_oracle(qc, problem_qubits, ancilla_qubits):
    a_low, a_high, b_low, b_high = problem_qubits[:4]
    qc.x(a_high)
    qc.x(b_low)
    qc.mcp(pi, [a_low, a_high, b_low], b_high)
    qc.x(b_low)
    qc.x(a_high)
```
