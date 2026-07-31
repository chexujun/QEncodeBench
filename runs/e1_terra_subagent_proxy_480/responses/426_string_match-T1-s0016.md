```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    from math import pi
    qc.x(problem_qubits[0]); qc.x(problem_qubits[3])
    qc.mcp(pi, problem_qubits[:4], problem_qubits[4])
    qc.x(problem_qubits[3]); qc.x(problem_qubits[0])
```
