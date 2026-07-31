```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    x0, x1, x2 = problem_qubits
    work = ancilla_qubits[0]

    qc.cz(x0, x1)
    qc.cz(x0, x2)
    qc.cz(x1, x2)

    qc.ccx(x0, x1, work)
    qc.cz(work, x2)
    qc.ccx(x0, x1, work)
```
