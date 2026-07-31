```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    q = problem_qubits[0]
    qc.x(q)
    qc.z(q)
    qc.x(q)
```
