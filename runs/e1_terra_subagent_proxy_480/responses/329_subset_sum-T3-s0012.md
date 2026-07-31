```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    target = ancilla_qubits[0]
    solutions = (0b00001, 0b01000, 0b00110)
    for solution in solutions:
        zero_controls = [problem_qubits[i] for i in range(5) if not ((solution >> i) & 1)]
        for qubit in zero_controls:
            qc.x(qubit)
        qc.mcx(problem_qubits, target)
        for qubit in reversed(zero_controls):
            qc.x(qubit)
```
