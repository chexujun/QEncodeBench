```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    flags = ancilla_qubits[:5]
    target = ancilla_qubits[5]

    for offset, flag in enumerate(flags):
        qc.x(problem_qubits[offset + 3])
        qc.mcx(
            [problem_qubits[offset], problem_qubits[offset + 1], problem_qubits[offset + 3]],
            flag,
        )
        qc.x(problem_qubits[offset + 3])

    qc.x(target)
    for flag in flags:
        qc.x(flag)
    qc.mcx(flags, target)
    for flag in flags:
        qc.x(flag)
    qc.z(target)
    for flag in flags:
        qc.x(flag)
    qc.mcx(flags, target)
    for flag in flags:
        qc.x(flag)
    qc.x(target)

    for offset, flag in reversed(list(enumerate(flags))):
        qc.x(problem_qubits[offset + 3])
        qc.mcx(
            [problem_qubits[offset], problem_qubits[offset + 1], problem_qubits[offset + 3]],
            flag,
        )
        qc.x(problem_qubits[offset + 3])
```
