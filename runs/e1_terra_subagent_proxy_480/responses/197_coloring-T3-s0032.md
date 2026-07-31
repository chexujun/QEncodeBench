```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    q = problem_qubits
    count0, count1, count2, flag = ancilla_qubits
    edges = [(0, 1), (0, 2), (0, 3), (0, 4), (1, 2), (2, 4), (3, 4)]

    def toggle_same_color(u, v):
        x, y = q[2 * u], q[2 * u + 1]
        z, w = q[2 * v], q[2 * v + 1]

        qc.x(flag)
        qc.cx(x, flag)
        qc.cx(y, flag)
        qc.cx(z, flag)
        qc.cx(w, flag)

        qc.cx(x, y)
        qc.cx(z, w)
        qc.mcx([x, y, w], flag)
        qc.mcx([z, y, w], flag)
        qc.cx(z, w)
        qc.cx(x, y)

    def increment_if_flag():
        qc.ccx(flag, count1, count2)
        qc.ccx(flag, count0, count1)
        qc.cx(flag, count0)

    def decrement_if_flag():
        qc.cx(flag, count0)
        qc.ccx(flag, count0, count1)
        qc.ccx(flag, count1, count2)

    for u, v in edges:
        toggle_same_color(u, v)
        increment_if_flag()
        toggle_same_color(u, v)

    qc.x(count0)
    qc.x(count1)
    qc.x(count2)
    qc.h(count2)
    qc.ccx(count0, count1, count2)
    qc.h(count2)
    qc.x(count2)
    qc.x(count1)
    qc.x(count0)

    for u, v in reversed(edges):
        toggle_same_color(u, v)
        decrement_if_flag()
        toggle_same_color(u, v)
```
