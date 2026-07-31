```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    x0, x1, x2 = problem_qubits
    flag = ancilla_qubits[0]

    qc.x(x0)
    qc.x(x1)
    qc.mcx([x0, x1, x2], flag)
    qc.z(flag)
    qc.mcx([x0, x1, x2], flag)
    qc.x(x1)
    qc.x(x0)
```
