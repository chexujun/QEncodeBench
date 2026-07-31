```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    target = ancilla_qubits[0]
    solutions = ((0, 2, 3), (0, 2, 4), (2, 3, 4))

    for selected in solutions:
        for i, qubit in enumerate(problem_qubits):
            if i not in selected:
                qc.x(qubit)
        qc.mcx(problem_qubits, target)
        for i, qubit in enumerate(problem_qubits):
            if i not in selected:
                qc.x(qubit)
```
