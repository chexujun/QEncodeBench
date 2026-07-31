```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    flags = ancilla_qubits[:5]
    target = ancilla_qubits[5]

    # Compute whether each length-4 window is 0000.
    for offset, flag in enumerate(flags):
        window = problem_qubits[offset:offset + 4]
        for q in window:
            qc.x(q)
        qc.mcx(window, flag)
        for q in reversed(window):
            qc.x(q)

    # Compute OR of the five match flags into target.
    for q in flags:
        qc.x(q)
    qc.mcx(flags, target)  # target = NOR(flags)
    for q in reversed(flags):
        qc.x(q)
    qc.x(target)           # target = OR(flags)

    qc.z(target)

    # Uncompute OR.
    qc.x(target)
    for q in flags:
        qc.x(q)
    qc.mcx(flags, target)
    for q in reversed(flags):
        qc.x(q)

    # Uncompute window-match flags.
    for offset, flag in reversed(list(enumerate(flags))):
        window = problem_qubits[offset:offset + 4]
        for q in window:
            qc.x(q)
        qc.mcx(window, flag)
        for q in reversed(window):
            qc.x(q)
```
