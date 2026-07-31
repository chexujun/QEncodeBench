```python
import math

def build_oracle(qc, problem_qubits, ancilla_qubits):
    s = problem_qubits
    a = ancilla_qubits[0]

    qc.mcx([s[2], s[3], s[4]], a)

    qc.mcp(math.pi, [a, s[1]])
    qc.mcp(math.pi, [a, s[5]])
    qc.mcp(math.pi, [a, s[1], s[5]])

    qc.mcx([s[2], s[3], s[4]], a)
```
