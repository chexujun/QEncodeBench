```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    edges = [(0, 1), (0, 4), (1, 2), (1, 4), (2, 3), (3, 4)]

    def add_pattern(controls, target, pattern):
        for qubit, bit in zip(controls, pattern):
            if bit == 0:
                qc.x(qubit)
        qc.mcx(controls, target)
        for qubit, bit in zip(controls, pattern):
            if bit == 0:
                qc.x(qubit)

    equal_patterns = [(0, 0, 0, 0), (0, 0, 1, 1), (1, 1, 0, 0), (1, 1, 1, 1), (0, 1, 0, 1), (1, 0, 1, 0)]
    for flag, (u, v) in zip(ancilla_qubits[:6], edges):
        controls = [problem_qubits[2 * u], problem_qubits[2 * u + 1], problem_qubits[2 * v], problem_qubits[2 * v + 1]]
        for pattern in equal_patterns:
            add_pattern(controls, flag, pattern)
    flags = list(ancilla_qubits[:6])
    for flag in flags: qc.x(flag)
    qc.h(flags[-1]); qc.mcx(flags[:-1], flags[-1]); qc.h(flags[-1])
    for flag in reversed(flags): qc.x(flag)
    for flag, (u, v) in reversed(list(zip(ancilla_qubits[:6], edges))):
        controls = [problem_qubits[2 * u], problem_qubits[2 * u + 1], problem_qubits[2 * v], problem_qubits[2 * v + 1]]
        for pattern in reversed(equal_patterns): add_pattern(controls, flag, pattern)
```
