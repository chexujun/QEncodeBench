```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    for i in (0, 3, 4):
        qc.x(problem_qubits[i])
    qc.mcx(problem_qubits, ancilla_qubits[0])
    for i in (0, 3, 4):
        qc.x(problem_qubits[i])
```
