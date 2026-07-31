```python
from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    edge_flags = ancilla_qubits[:6]
    scratch = ancilla_qubits[6]

    edges = (
        (0, 2),
        (0, 4),
        (1, 2),
        (1, 4),
        (2, 3),
        (2, 4),
    )

    def toggle_edge_difference(u: int, v: int, target: int) -> None:
        a0 = problem_qubits[2 * u]
        a1 = problem_qubits[2 * u + 1]
        b0 = problem_qubits[2 * v]
        b1 = problem_qubits[2 * v + 1]

        # scratch = a0 XOR a1
        qc.cx(a0, scratch)
        qc.cx(a1, scratch)

        # Toggle target iff the decoded colors differ.
        qc.cx(scratch, target)
        qc.cx(b0, target)
        qc.cx(b1, target)
        qc.ccx(scratch, b0, target)
        qc.mcx([scratch, a0, b0], target)
        qc.mcx([scratch, a0, b1], target)
        qc.mcx([scratch, b0, b1], target)

        # Restore scratch to |0>.
        qc.cx(a1, scratch)
        qc.cx(a0, scratch)

    for (u, v), flag in zip(edges, edge_flags):
        toggle_edge_difference(u, v, flag)

    # Mark exactly when all six edge constraints are satisfied.
    qc.mcx(edge_flags, scratch)
    qc.z(scratch)
    qc.mcx(edge_flags, scratch)

    for (u, v), flag in reversed(tuple(zip(edges, edge_flags))):
        toggle_edge_difference(u, v, flag)
```
