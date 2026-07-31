```python
import math

def build_oracle(qc, problem_qubits, ancilla_qubits):
    edges = ((0, 1), (0, 2), (0, 4),
             (1, 2), (1, 3), (1, 4))
    flags = ancilla_qubits[:6]

    def toggle_different(u, v, target):
        u0 = problem_qubits[2 * u]
        u1 = problem_qubits[2 * u + 1]
        v0 = problem_qubits[2 * v]
        v1 = problem_qubits[2 * v + 1]

        qc.x(u0)
        qc.x(u1)
        qc.x(v0)
        qc.x(v1)

        qc.ccx(u1, v0, target)
        qc.ccx(u0, v1, target)

        qc.mcx([u0, u1, v0], target)
        qc.mcx([u0, u1, v1], target)
        qc.mcx([u0, v0, v1], target)
        qc.mcx([u1, v0, v1], target)

        qc.cx(u0, target)
        qc.cx(u1, target)
        qc.cx(v0, target)
        qc.cx(v1, target)

    for edge, flag in zip(edges, flags):
        toggle_different(edge[0], edge[1], flag)

    qc.mcp(math.pi, flags[:-1], flags[-1])

    for edge, flag in reversed(list(zip(edges, flags))):
        toggle_different(edge[0], edge[1], flag)
```
