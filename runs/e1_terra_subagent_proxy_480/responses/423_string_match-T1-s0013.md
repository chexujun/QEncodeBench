```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    qc.x(problem_qubits[0]); qc.x(problem_qubits[4]); qc.h(problem_qubits[5])
    qc.mcx([problem_qubits[0],problem_qubits[1],problem_qubits[2],problem_qubits[3],problem_qubits[4]],problem_qubits[5],ancilla_qubits=[ancilla_qubits[0]],mode="recursion")
    qc.h(problem_qubits[5]); qc.x(problem_qubits[4]); qc.x(problem_qubits[0])
```
