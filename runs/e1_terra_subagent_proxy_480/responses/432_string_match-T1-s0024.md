```python
from math import pi
def build_oracle(qc, problem_qubits, ancilla_qubits):
    for i in (1, 2, 4): qc.x(problem_qubits[i])
    qc.mcp(pi, problem_qubits[:4], problem_qubits[4])
    for i in (1, 2, 4): qc.x(problem_qubits[i])
```
