```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    counter = list(ancilla_qubits[:4])
    work = ancilla_qubits[4]

    equal_patterns = (
        (0, 0, 0, 0), (0, 0, 1, 1),
        (1, 1, 0, 0), (1, 1, 1, 1),
        (1, 0, 1, 0), (0, 1, 0, 1),
    )

    def toggle_equal(u, v):
        qs = [problem_qubits[2 * u], problem_qubits[2 * u + 1],
              problem_qubits[2 * v], problem_qubits[2 * v + 1]]
        for pattern in equal_patterns:
            flipped = [q for q, bit in zip(qs, pattern) if bit == 0]
            for q in flipped:
                qc.x(q)
            qc.mcx(qs, work)
            for q in flipped:
                qc.x(q)

    def increment():
        for i in range(3, 0, -1):
            qc.mcx([work] + counter[:i], counter[i])
        qc.cx(work, counter[0])

    def decrement():
        qc.cx(work, counter[0])
        for i in range(1, 4):
            qc.mcx([work] + counter[:i], counter[i])

    edges = ((0, 1), (0, 4), (0, 5), (1, 3),
             (1, 5), (2, 3), (3, 4), (4, 5))

    for u, v in edges:
        toggle_equal(u, v)
        increment()
        toggle_equal(u, v)

    for q in counter:
        qc.x(q)
    qc.h(work)
    qc.mcx(counter, work)
    qc.h(work)
    for q in counter:
        qc.x(q)

    for u, v in reversed(edges):
        toggle_equal(u, v)
        decrement()
        toggle_equal(u, v)
```
