```python
import math
from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    def toggle_equal(a0: int, a1: int, b0: int, b1: int, target: int) -> None:
        # Algebraic-normal form of:
        # decode(a0 + 2*a1) == decode(b0 + 2*b1), with 3 decoded as 0.
        qc.x(target)
        qc.cx(a0, target)
        qc.cx(a1, target)
        qc.cx(b0, target)
        qc.ccx(a1, b0, target)
        qc.mcx([a0, a1, b0], target)
        qc.cx(b1, target)
        qc.ccx(a0, b1, target)
        qc.mcx([a0, a1, b1], target)
        qc.mcx([a0, b0, b1], target)
        qc.mcx([a1, b0, b1], target)

    edges = ((0, 2), (0, 4), (1, 3), (2, 4))
    flags = ancilla_qubits[:4]

    for (u, v), flag in zip(edges, flags):
        toggle_equal(
            problem_qubits[2 * u],
            problem_qubits[2 * u + 1],
            problem_qubits[2 * v],
            problem_qubits[2 * v + 1],
            flag,
        )
        qc.x(flag)  # Flag is 1 exactly when this edge has different colors.

    qc.mcp(math.pi, flags[:3], flags[3])

    for (u, v), flag in reversed(list(zip(edges, flags))):
        qc.x(flag)
        toggle_equal(
            problem_qubits[2 * u],
            problem_qubits[2 * u + 1],
            problem_qubits[2 * v],
            problem_qubits[2 * v + 1],
            flag,
        )
```
