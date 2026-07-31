```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    flag = ancilla_qubits[0]
    solutions = ((0, 1, 3), (0, 2, 3), (3, 4))

    for selected in solutions:
        zeros = [problem_qubits[i] for i in range(5) if i not in selected]
        for qubit in zeros:
            qc.x(qubit)
        qc.mcx(problem_qubits, flag)
        for qubit in zeros:
            qc.x(qubit)
```
