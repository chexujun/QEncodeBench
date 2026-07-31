```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    flags = ancilla_qubits[:5]
    work = ancilla_qubits[5]

    for offset, flag in enumerate(flags):
        window = problem_qubits[offset:offset + 4]
        qc.x(window[0])
        qc.x(window[1])
        qc.mcx(window, flag)
        qc.x(window[1])
        qc.x(window[0])

    for flag in flags:
        qc.x(flag)
    qc.mcx(flags, work)
    qc.z(work)
    qc.mcx(flags, work)
    for flag in flags:
        qc.x(flag)

    for offset, flag in reversed(list(enumerate(flags))):
        window = problem_qubits[offset:offset + 4]
        qc.x(window[0])
        qc.x(window[1])
        qc.mcx(window, flag)
        qc.x(window[1])
        qc.x(window[0])
```
