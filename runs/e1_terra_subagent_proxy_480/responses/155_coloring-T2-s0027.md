```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    edges = [(0, 1), (0, 2), (0, 3), (2, 3), (2, 4)]
    flags = ancilla_qubits[:5]
    phase = ancilla_qubits[5]

    equal_codes = [(0, 0), (0, 3), (3, 0), (3, 3), (1, 1), (2, 2)]

    for flag, (u, v) in zip(flags, edges):
        controls = [
            problem_qubits[2 * u], problem_qubits[2 * u + 1],
            problem_qubits[2 * v], problem_qubits[2 * v + 1],
        ]
        for a, b in equal_codes:
            state = a | (b << 2)
            qc.mcx(controls, flag, ctrl_state=state)

    for flag in flags:
        qc.x(flag)

    qc.x(phase)
    qc.h(phase)
    qc.mcx(flags, phase)
    qc.h(phase)
    qc.x(phase)

    for flag in flags:
        qc.x(flag)

    for flag, (u, v) in reversed(list(zip(flags, edges))):
        controls = [
            problem_qubits[2 * u], problem_qubits[2 * u + 1],
            problem_qubits[2 * v], problem_qubits[2 * v + 1],
        ]
        for a, b in reversed(equal_codes):
            state = a | (b << 2)
            qc.mcx(controls, flag, ctrl_state=state)
```
