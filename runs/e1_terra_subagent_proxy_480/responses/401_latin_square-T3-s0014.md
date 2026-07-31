```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    for i in (0, 1, 2, 4, 6, 7):
        qc.x(problem_qubits[i])
    qc.mcp(3.141592653589793, problem_qubits[:7], problem_qubits[7])
    for i in (0, 1, 2, 4, 6, 7):
        qc.x(problem_qubits[i])
```
