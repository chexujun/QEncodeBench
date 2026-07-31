```python
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = ((0, 1), (0, 2), (0, 4),
             (1, 3), (2, 4), (3, 4))
    edge_flags = ancilla_qubits[:6]
    phase_ancilla = ancilla_qubits[6]

    def toggle_edge_valid(u: int, v: int, target: int) -> None:
        u_low = problem_qubits[2 * u]
        u_high = problem_qubits[2 * u + 1]
        v_low = problem_qubits[2 * v]
        v_high = problem_qubits[2 * v + 1]

        # Temporarily replace each low bit by low XOR high.  This bit is
        # zero exactly for decoded color 0, and one for colors 1 or 2.
        qc.cx(u_high, u_low)
        qc.cx(v_high, v_low)

        # The decoded colors differ iff their parity bits differ, or both
        # parity bits are one and their high bits differ.
        qc.cx(u_low, target)
        qc.cx(v_low, target)
        qc.mcx([u_low, v_low, u_high], target)
        qc.mcx([u_low, v_low, v_high], target)

        qc.cx(v_high, v_low)
        qc.cx(u_high, u_low)

    # Compute one validity bit for each edge.
    for (u, v), flag in zip(edges, edge_flags):
        toggle_edge_valid(u, v, flag)

    # Apply a phase exactly when all six edge-validity bits are one.
    qc.mcx(edge_flags, phase_ancilla)
    qc.z(phase_ancilla)
    qc.mcx(edge_flags, phase_ancilla)

    # Uncompute every edge flag.
    for (u, v), flag in reversed(tuple(zip(edges, edge_flags))):
        toggle_edge_valid(u, v, flag)
```
