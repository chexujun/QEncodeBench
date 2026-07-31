```python
from math import pi
from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    # Four ancillas hold whether the corresponding edge has equal endpoint colors.
    flags = ancilla_qubits[:4]
    edges = ((0, 1), (0, 2), (0, 3), (1, 2))

    def toggle_equal_color(a0: int, a1: int, b0: int, b1: int, target: int) -> None:
        # ANF of:
        # (a0 + 2*a1) % 3 == (b0 + 2*b1) % 3
        bits = (a0, a1, b0, b1)
        qc.x(target)
        qc.cx(a0, target)
        qc.cx(a1, target)
        qc.cx(b0, target)
        qc.cx(b1, target)
        qc.ccx(a1, b0, target)
        qc.ccx(a0, b1, target)
        qc.mcx([a0, a1, b0], target)
        qc.mcx([a0, a1, b1], target)
        qc.mcx([a0, b0, b1], target)
        qc.mcx([a1, b0, b1], target)

    for flag, (u, v) in zip(flags, edges):
        toggle_equal_color(
            problem_qubits[2 * u],
            problem_qubits[2 * u + 1],
            problem_qubits[2 * v],
            problem_qubits[2 * v + 1],
            flag,
        )

    # A valid coloring has no equal-color edge.
    for flag in flags:
        qc.x(flag)
    qc.mcp(pi, flags[:3], flags[3])
    for flag in flags:
        qc.x(flag)

    for flag, (u, v) in reversed(tuple(zip(flags, edges))):
        toggle_equal_color(
            problem_qubits[2 * u],
            problem_qubits[2 * u + 1],
            problem_qubits[2 * v],
            problem_qubits[2 * v + 1],
            flag,
        )
```
