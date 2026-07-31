```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    from math import pi

    for i in (0, 1, 2, 4):
        qc.x(problem_qubits[i])
    qc.mcp(pi, [problem_qubits[i] for i in (0, 1, 2, 4)], problem_qubits[3])
    for i in (0, 1, 2, 4):
        qc.x(problem_qubits[i])
```
