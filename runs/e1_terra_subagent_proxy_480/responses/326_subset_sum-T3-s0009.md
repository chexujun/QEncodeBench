```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    target = ancilla_qubits[0]
    solutions = ((1, 0, 1, 0, 0), (1, 0, 0, 0, 1), (0, 0, 1, 0, 1))
    for solution in solutions:
        zero_controls = [problem_qubits[i] for i, bit in enumerate(solution) if bit == 0]
        qc.x(zero_controls)
        qc.mcx(problem_qubits, target)
        qc.x(zero_controls)
```
