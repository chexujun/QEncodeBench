```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    target = problem_qubits[5]

    qc.x(target)
    qc.h(target)
    qc.mcx(problem_qubits[:5], target)
    qc.h(target)
    qc.x(target)
```
