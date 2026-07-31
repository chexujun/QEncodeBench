```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    flags = ancilla_qubits[:5]
    output = ancilla_qubits[5]

    def compute_matches():
        for offset, flag in enumerate(flags):
            qc.x(problem_qubits[offset])
            qc.x(problem_qubits[offset + 1])
            qc.mcx(
                [problem_qubits[offset], problem_qubits[offset + 1],
                 problem_qubits[offset + 3]],
                flag,
            )
            qc.x(problem_qubits[offset + 1])
            qc.x(problem_qubits[offset])

    compute_matches()

    qc.x(output)
    for flag in flags:
        qc.x(flag)
    qc.mcx(flags, output)
    for flag in reversed(flags):
        qc.x(flag)

    qc.z(output)

    for flag in flags:
        qc.x(flag)
    qc.mcx(flags, output)
    for flag in reversed(flags):
        qc.x(flag)
    qc.x(output)

    compute_matches()
```
