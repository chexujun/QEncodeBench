```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    x0, x1, x2 = problem_qubits
    qc.cz(x0, x2)
    qc.cz(x1, x2)
```
