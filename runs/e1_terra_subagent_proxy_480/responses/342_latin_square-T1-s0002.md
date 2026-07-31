```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    qc.x(problem_qubits[1])
    qc.x(problem_qubits[2])
    qc.x(problem_qubits[3])
    qc.mcp(3.141592653589793, problem_qubits[:4])
    qc.x(problem_qubits[1])
    qc.x(problem_qubits[2])
    qc.x(problem_qubits[3])
```
