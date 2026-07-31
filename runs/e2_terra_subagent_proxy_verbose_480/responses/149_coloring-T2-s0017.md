```python
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edge_flags = ancilla_qubits[:5]
    phase_ancilla = ancilla_qubits[5]
    edges = ((0, 1), (0, 3), (1, 2), (1, 3), (2, 3))

    def toggle_colors_differ(u: int, v: int, target: int) -> None:
        u0 = problem_qubits[2 * u]
        u1 = problem_qubits[2 * u + 1]
        v0 = problem_qubits[2 * v]
        v1 = problem_qubits[2 * v + 1]

        # Algebraic-normal-form implementation of decoded_color(u) !=
        # decoded_color(v), where both 00 and 11 decode to color zero.
        qc.cx(u0, target)
        qc.cx(u1, target)
        qc.cx(v0, target)
        qc.cx(v1, target)

        qc.ccx(u1, v0, target)
        qc.ccx(u0, v1, target)

        qc.mcx([u0, u1, v0], target)
        qc.mcx([u0, v0, v1], target)
        qc.mcx([u0, u1, v1], target)
        qc.mcx([u1, v0, v1], target)

    # Compute one "colors differ" flag for each edge.
    for (u, v), flag in zip(edges, edge_flags):
        toggle_colors_differ(u, v, flag)

    # Mark exactly when all five edge constraints hold.
    qc.mcx(edge_flags, phase_ancilla)
    qc.z(phase_ancilla)
    qc.mcx(edge_flags, phase_ancilla)

    # Uncompute all edge flags.
    for (u, v), flag in reversed(list(zip(edges, edge_flags))):
        toggle_colors_differ(u, v, flag)
```
