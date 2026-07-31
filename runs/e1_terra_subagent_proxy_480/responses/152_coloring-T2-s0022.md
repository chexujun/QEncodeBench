```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    flags = ancilla_qubits[:6]
    edges = [(0, 1), (0, 2), (0, 4), (1, 2), (1, 3), (1, 4)]

    def compute_equal(u, v, target):
        a0, a1 = problem_qubits[2 * u], problem_qubits[2 * u + 1]
        b0, b1 = problem_qubits[2 * v], problem_qubits[2 * v + 1]

        qc.cx(a0, a1)
        qc.cx(b0, b1)

        qc.x(a1)
        qc.x(b1)
        qc.ccx(a1, b1, target)
        qc.x(b1)
        qc.x(a1)

        qc.cx(a0, b0)
        qc.x(b0)
        qc.mcx([a1, b1, b0], target)
        qc.x(b0)
        qc.cx(a0, b0)

        qc.cx(b0, b1)
        qc.cx(a0, a1)

    for edge, flag in zip(edges, flags):
        compute_equal(*edge, flag)

    for flag in flags:
        qc.x(flag)
    qc.mcp(3.141592653589793, flags[:5], flags[5])
    for flag in reversed(flags):
        qc.x(flag)

    for edge, flag in reversed(list(zip(edges, flags))):
        compute_equal(*edge, flag)
```
