```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    qc.x(problem_qubits[2])
    qc.x(problem_qubits[4])
    qc.mcx(list(problem_qubits), ancilla_qubits[0])
    qc.x(problem_qubits[4])
    qc.x(problem_qubits[2])
```
