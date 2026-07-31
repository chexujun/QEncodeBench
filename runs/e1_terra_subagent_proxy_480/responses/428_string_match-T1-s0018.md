```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    controls = [problem_qubits[1], problem_qubits[3], problem_qubits[4], problem_qubits[5]]
    target = ancilla_qubits[0]
    qc.x(problem_qubits[1]); qc.x(problem_qubits[4]); qc.x(problem_qubits[5])
    qc.mcx(controls, target); qc.z(target); qc.mcx(controls, target)
    qc.x(problem_qubits[5]); qc.x(problem_qubits[4]); qc.x(problem_qubits[1])
```
