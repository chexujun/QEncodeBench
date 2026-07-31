```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    from math import pi

    q = list(problem_qubits)
    for i in (0, 2, 3):
        qc.x(q[i])
    qc.mcp(pi, q[:3], q[3])
    for i in (0, 2, 3):
        qc.x(q[i])
    return qc
```
