```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    edges = [(0, 1), (0, 2), (0, 3), (0, 4),
             (1, 4), (2, 3), (2, 4)]
    flags = list(ancilla_qubits[:7])

    def conflict(v, w, target):
        a0, a1 = problem_qubits[2 * v], problem_qubits[2 * v + 1]
        b0, b1 = problem_qubits[2 * w], problem_qubits[2 * w + 1]

        qc.cx(a0, a1)
        qc.cx(b0, b1)
        qc.x(a1)
        qc.x(b1)
        qc.mcx([a1, b1], target)
        qc.x(b1)
        qc.x(a1)
        qc.cx(b0, b1)
        qc.cx(a0, a1)

        qc.x(a0)
        qc.x(b0)
        qc.mcx([a0, a1, b0, b1], target)
        qc.x(b0)
        qc.x(a0)

        qc.x(a1)
        qc.x(b1)
        qc.mcx([a0, a1, b0, b1], target)
        qc.x(b1)
        qc.x(a1)

    for (v, w), flag in zip(edges, flags):
        conflict(v, w, flag)

    for flag in flags:
        qc.x(flag)
    qc.h(flags[-1])
    qc.mcx(flags[:-1], flags[-1])
    qc.h(flags[-1])
    for flag in reversed(flags):
        qc.x(flag)

    for (v, w), flag in reversed(list(zip(edges, flags))):
        conflict(v, w, flag)
```
