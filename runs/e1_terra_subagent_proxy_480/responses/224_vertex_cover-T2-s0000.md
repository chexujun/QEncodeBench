```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    target = problem_qubits[4]
    for i in (1, 2, 4):
        qc.x(problem_qubits[i])
    qc.h(target)
    qc.mcx(problem_qubits[:4], target, mode="noancilla")
    qc.h(target)
    for i in (1, 2, 4):
        qc.x(problem_qubits[i])
```
