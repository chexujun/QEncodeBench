```python
import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edge_flags = ancilla_qubits[:4]
    phase_aux = ancilla_qubits[4]

    def toggle_same_color(v1, v2, target):
        a0, a1 = problem_qubits[2 * v1], problem_qubits[2 * v1 + 1]
        b0, b1 = problem_qubits[2 * v2], problem_qubits[2 * v2 + 1]

        # Both decode to color 0: codes are 00 or 11.
        qc.cx(a1, a0)
        qc.cx(b1, b0)
        qc.x(a0)
        qc.x(b0)
        qc.ccx(a0, b0, target)
        qc.x(b0)
        qc.x(a0)
        qc.cx(b1, b0)
        qc.cx(a1, a0)

        # Both decode to color 1: code 01.
        qc.x(a1)
        qc.x(b1)
        qc.mcx([a0, a1, b0, b1], target)
        qc.x(b1)
        qc.x(a1)

        # Both decode to color 2: code 10.
        qc.x(a0)
        qc.x(b0)
        qc.mcx([a0, a1, b0, b1], target)
        qc.x(b0)
        qc.x(a0)

    edges = [(0, 3), (1, 2), (1, 3), (2, 3)]

    for (u, v), flag in zip(edges, edge_flags):
        toggle_same_color(u, v, flag)

    # A valid coloring has no monochromatic edge.
    for flag in edge_flags:
        qc.x(flag)
    qc.x(phase_aux)
    qc.mcp(math.pi, edge_flags, phase_aux)
    qc.x(phase_aux)
    for flag in reversed(edge_flags):
        qc.x(flag)

    for (u, v), flag in reversed(list(zip(edges, edge_flags))):
        toggle_same_color(u, v, flag)
```
