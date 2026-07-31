```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    target = ancilla_qubits[0]
    for selected in ((0, 1), (0, 3)):
        for i in range(4):
            if i not in selected:
                qc.x(problem_qubits[i])
        qc.h(target)
        qc.mcx(problem_qubits, target)
        qc.h(target)
        for i in range(4):
            if i not in selected:
                qc.x(problem_qubits[i])
```
