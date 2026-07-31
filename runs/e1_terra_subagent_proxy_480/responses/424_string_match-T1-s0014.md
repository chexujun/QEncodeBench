```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    qc.x(problem_qubits[0]); qc.h(ancilla_qubits[0]); qc.ccx(problem_qubits[0], problem_qubits[2], ancilla_qubits[0]); qc.h(ancilla_qubits[0]); qc.x(problem_qubits[0])
```
