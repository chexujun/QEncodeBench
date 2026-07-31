```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    qc.x(problem_qubits[0])
    qc.ccz(problem_qubits[0], problem_qubits[1], problem_qubits[2])
    qc.x(problem_qubits[0])
```
