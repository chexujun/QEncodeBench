```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    x0, x1 = problem_qubits[2], problem_qubits[3]
    y0, y1 = problem_qubits[8], problem_qubits[9]
    qc.x(x0)
    qc.x(y0)
    qc.x(y1)
    qc.h(x1)
    qc.mcx([x0, y0, y1], x1)
    qc.h(x1)
    qc.x(y1)
    qc.x(y0)
    qc.x(x0)
```
