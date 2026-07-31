```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    edges = [(0, 1), (0, 2), (0, 3), (0, 4), (1, 4), (2, 3), (3, 4)]
    flags = ancilla_qubits[:7]
    work = ancilla_qubits[7]

    def conflict(a, b, target):
        x0, x1 = problem_qubits[2 * a], problem_qubits[2 * a + 1]
        y0, y1 = problem_qubits[2 * b], problem_qubits[2 * b + 1]

        qc.x(target)
        qc.cx(x0, target)
        qc.cx(x1, target)
        qc.cx(y0, target)
        qc.cx(y1, target)
        for u in (x0, x1):
            for v in (y0, y1):
                qc.ccx(u, v, target)

        qc.x(x0)
        qc.x(y0)
        qc.mcx([x0, x1, y0, y1], target)
        qc.x(y0)
        qc.x(x0)

        qc.x(x1)
        qc.x(y0)
        qc.mcx([x0, x1, y0, y1], target)
        qc.x(y0)
        qc.x(x1)

    for (a, b), flag in zip(edges, flags):
        conflict(a, b, flag)

    qc.mcx(flags, work)
    qc.z(work)
    qc.mcx(flags, work)

    for (a, b), flag in reversed(list(zip(edges, flags))):
        conflict(a, b, flag)
```
