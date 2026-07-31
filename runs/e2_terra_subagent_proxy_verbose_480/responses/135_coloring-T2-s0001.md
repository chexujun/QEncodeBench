```python
from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    def toggle_equal(a0, a1, b0, b1, target):
        # Both vertices decode to color 0 iff their two code bits are equal.
        qc.cx(a0, a1)
        qc.cx(b0, b1)
        qc.x(a1)
        qc.x(b1)
        qc.ccx(a1, b1, target)
        qc.x(b1)
        qc.x(a1)
        qc.cx(b0, b1)
        qc.cx(a0, a1)

        # Both vertices decode to color 1: codes 01 and 01.
        qc.x(a1)
        qc.x(b1)
        qc.mcx([a0, a1, b0, b1], target)
        qc.x(b1)
        qc.x(a1)

        # Both vertices decode to color 2: codes 10 and 10.
        qc.x(a0)
        qc.x(b0)
        qc.mcx([a0, a1, b0, b1], target)
        qc.x(b0)
        qc.x(a0)

    edges = [(0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]
    edge_flags = ancilla_qubits[:5]

    # Compute one "colors differ" flag for each edge.
    for (u, v), flag in zip(edges, edge_flags):
        toggle_equal(
            problem_qubits[2 * u],
            problem_qubits[2 * u + 1],
            problem_qubits[2 * v],
            problem_qubits[2 * v + 1],
            flag,
        )
        qc.x(flag)

    # Apply -1 exactly when all five edge constraints hold.
    qc.h(edge_flags[-1])
    qc.mcx(edge_flags[:-1], edge_flags[-1])
    qc.h(edge_flags[-1])

    # Uncompute all ancillas.
    for (u, v), flag in reversed(list(zip(edges, edge_flags))):
        qc.x(flag)
        toggle_equal(
            problem_qubits[2 * u],
            problem_qubits[2 * u + 1],
            problem_qubits[2 * v],
            problem_qubits[2 * v + 1],
            flag,
        )
```
