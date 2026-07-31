```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    patterns = (
        (0, 0, 0, 1, 0, 0, 1, 0),
        (0, 0, 0, 1, 1, 1, 1, 0),
        (1, 1, 0, 1, 0, 0, 1, 0),
        (1, 1, 0, 1, 1, 1, 1, 0),
    )
    controls = list(problem_qubits[:7])
    target = problem_qubits[7]

    for pattern in patterns:
        zeros = [problem_qubits[i] for i, bit in enumerate(pattern) if bit == 0]
        for qubit in zeros:
            qc.x(qubit)
        qc.h(target)
        qc.mcx(controls, target, ancilla_qubits[:5], mode="v-chain")
        qc.h(target)
        for qubit in reversed(zeros):
            qc.x(qubit)
```
