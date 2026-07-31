```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    from math import pi

    target = problem_qubits[-1]
    controls = problem_qubits[:-1]

    for qubit, bit in zip(problem_qubits, (0, 1, 0, 1)):
        if bit == 0:
            qc.x(qubit)

    qc.mcp(pi, controls, target)

    for qubit, bit in zip(problem_qubits, (0, 1, 0, 1)):
        if bit == 0:
            qc.x(qubit)
```
