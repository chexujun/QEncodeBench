```python
import math

def build_oracle(qc, problem_qubits, ancilla_qubits):
    flags = ancilla_qubits[:5]

    def toggle_equality(a0, a1, b0, b1, target):
        # Both vertices decode to color 0 iff each code has equal bits.
        qc.cx(a0, a1)
        qc.cx(b0, b1)
        qc.x(a1)
        qc.x(b1)
        qc.ccx(a1, b1, target)
        qc.x(b1)
        qc.x(a1)
        qc.cx(b0, b1)
        qc.cx(a0, a1)

        # Both vertices decode to color 1: 01 and 01.
        qc.x(a0)
        qc.x(b0)
        qc.mcx([a0, a1, b0, b1], target)
        qc.x(b0)
        qc.x(a0)

        # Both vertices decode to color 2: 10 and 10.
        qc.x(a1)
        qc.x(b1)
        qc.mcx([a0, a1, b0, b1], target)
        qc.x(b1)
        qc.x(a1)

    edges = [(0, 1), (0, 2), (0, 3), (1, 2), (2, 3)]

    for (u, v), flag in zip(edges, flags):
        toggle_equality(
            problem_qubits[2 * u],
            problem_qubits[2 * u + 1],
            problem_qubits[2 * v],
            problem_qubits[2 * v + 1],
            flag,
        )

    # Each flag is one exactly for a monochromatic edge.
    # Mark precisely when every edge is non-monochromatic.
    for flag in flags:
        qc.x(flag)
    qc.mcp(math.pi, flags[:-1], flags[-1])
    for flag in reversed(flags):
        qc.x(flag)

    for (u, v), flag in reversed(list(zip(edges, flags))):
        toggle_equality(
            problem_qubits[2 * u],
            problem_qubits[2 * u + 1],
            problem_qubits[2 * v],
            problem_qubits[2 * v + 1],
            flag,
        )
```
