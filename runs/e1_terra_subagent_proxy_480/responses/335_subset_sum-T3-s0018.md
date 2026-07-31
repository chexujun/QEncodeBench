```python
def build_oracle(qc, problem_qubits, ancilla_qubits) -> None:
    qc.x(problem_qubits[0])
    qc.mcp(3.141592653589793, problem_qubits[:4], problem_qubits[4])
    qc.x(problem_qubits[0])
```
