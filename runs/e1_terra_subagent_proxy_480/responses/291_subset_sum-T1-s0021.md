```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    qc.x(problem_qubits[0])
    qc.x(problem_qubits[1])
    qc.mcp(3.141592653589793, problem_qubits[:2], problem_qubits[2])
    qc.x(problem_qubits[1])
    qc.x(problem_qubits[0])
```
