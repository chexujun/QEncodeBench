```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    zeros = [0, 2, 3, 5, 6, 7]
    for i in zeros: qc.x(problem_qubits[i])
    qc.h(problem_qubits[7]); qc.mcx(problem_qubits[:7], problem_qubits[7]); qc.h(problem_qubits[7])
    for i in zeros: qc.x(problem_qubits[i])
```
