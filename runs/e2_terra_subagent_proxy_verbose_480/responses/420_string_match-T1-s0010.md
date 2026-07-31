```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    x0, x1, _, x3 = problem_qubits
    a = ancilla_qubits[0]

    qc.x(x0)
    qc.ccx(x1, x3, a)
    qc.cz(x0, a)
    qc.ccx(x1, x3, a)
    qc.x(x0)
```
