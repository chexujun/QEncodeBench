```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    marked = (
        (0, 1, 0, 1, 1),
        (0, 1, 1, 0, 1),
        (1, 0, 1, 1, 0),
        (1, 1, 0, 0, 1),
    )
    target = problem_qubits[-1]
    controls = problem_qubits[:-1]

    for bits in marked:
        for qubit, bit in zip(problem_qubits, bits):
            if bit == 0:
                qc.x(qubit)
        qc.h(target)
        qc.mcx(controls, target)
        qc.h(target)
        for qubit, bit in zip(problem_qubits, bits):
            if bit == 0:
                qc.x(qubit)
```
