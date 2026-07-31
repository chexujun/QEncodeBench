```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    for qubit in problem_qubits[1:]:
        qc.x(qubit)
    qc.mcx(problem_qubits, ancilla_qubits[0])
    for qubit in problem_qubits[1:]:
        qc.x(qubit)
```
