```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    target = ancilla_qubits[0]
    qc.x(problem_qubits[2])
    qc.x(problem_qubits[4])
    qc.mcx(problem_qubits, target)
    qc.x(problem_qubits[4])
    qc.x(problem_qubits[2])
    qc.x(problem_qubits[1])
    qc.x(problem_qubits[3])
    qc.mcx(problem_qubits, target)
    qc.x(problem_qubits[3])
    qc.x(problem_qubits[1])
```
