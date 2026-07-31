```python
def build_oracle(qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]) -> None:
    flags = ancilla_qubits[:5]
    result = ancilla_qubits[5]

    # Compute whether the pattern 1110 starts at each possible offset.
    for offset, flag in enumerate(flags):
        qc.x(problem_qubits[offset + 3])
        qc.mcx(
            [
                problem_qubits[offset],
                problem_qubits[offset + 1],
                problem_qubits[offset + 2],
                problem_qubits[offset + 3],
            ],
            flag,
        )
        qc.x(problem_qubits[offset + 3])

    # Compute OR(flags) into result.
    qc.x(result)
    for flag in flags:
        qc.x(flag)
    qc.mcx(flags, result)
    for flag in flags:
        qc.x(flag)

    qc.z(result)

    # Uncompute OR(flags).
    for flag in flags:
        qc.x(flag)
    qc.mcx(flags, result)
    for flag in flags:
        qc.x(flag)
    qc.x(result)

    # Uncompute match flags.
    for offset, flag in reversed(list(enumerate(flags))):
        qc.x(problem_qubits[offset + 3])
        qc.mcx(
            [
                problem_qubits[offset],
                problem_qubits[offset + 1],
                problem_qubits[offset + 2],
                problem_qubits[offset + 3],
            ],
            flag,
        )
        qc.x(problem_qubits[offset + 3])
```
