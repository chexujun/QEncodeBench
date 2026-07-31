```python
import math

from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    # Computes whether endpoints u and v have the same decoded color into target.
    # The Boolean expression is implemented in algebraic normal form.
    def same_color(u: int, v: int, target: int) -> None:
        a = problem_qubits[2 * u]
        A = problem_qubits[2 * u + 1]
        b = problem_qubits[2 * v]
        B = problem_qubits[2 * v + 1]

        qc.x(target)
        qc.cx(a, target)
        qc.cx(A, target)
        qc.cx(b, target)
        qc.cx(B, target)
        qc.mcx([a, B], target)
        qc.mcx([A, b], target)
        qc.mcx([a, A, b], target)
        qc.mcx([a, A, B], target)
        qc.mcx([a, b, B], target)
        qc.mcx([A, b, B], target)

    edge_flags = ancilla_qubits[:3]

    same_color(0, 1, edge_flags[0])
    same_color(0, 2, edge_flags[1])
    same_color(2, 3, edge_flags[2])

    qc.x(edge_flags)
    qc.mcp(math.pi, edge_flags[:2], edge_flags[2])
    qc.x(edge_flags)

    same_color(2, 3, edge_flags[2])
    same_color(0, 2, edge_flags[1])
    same_color(0, 1, edge_flags[0])
```
