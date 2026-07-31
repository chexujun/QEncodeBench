```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    lows = [problem_qubits[0], problem_qubits[2], problem_qubits[4]]
    highs = [problem_qubits[1], problem_qubits[3], problem_qubits[5]]

    for qubit in lows:
        qc.x(qubit)

    target = highs[-1]
    qc.h(target)
    qc.mcx(lows + highs[:-1], target)
    qc.h(target)

    for qubit in lows:
        qc.x(qubit)
```
