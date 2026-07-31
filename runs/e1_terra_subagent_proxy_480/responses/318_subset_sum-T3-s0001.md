```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    qc.cx(problem_qubits[3], ancilla_qubits[0])
```
