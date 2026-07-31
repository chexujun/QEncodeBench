```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    qc.x(problem_qubits[1])
    qc.cz(problem_qubits[1], problem_qubits[3])
    qc.x(problem_qubits[1])
```
