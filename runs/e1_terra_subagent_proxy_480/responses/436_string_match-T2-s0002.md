```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    for offset in range(3):
        a, b, c = problem_qubits[offset : offset + 3]
        qc.x(c)
        qc.mcp(3.141592653589793, [a, b], c)
        qc.x(c)
```
