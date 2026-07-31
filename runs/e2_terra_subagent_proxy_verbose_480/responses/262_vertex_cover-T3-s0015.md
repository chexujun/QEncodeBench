```python
from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    # Nine ancillas flag uncovered edges; the last three hold a 3-bit
    # reversible population count of selected vertices.
    edge_flags = ancilla_qubits[:9]
    c0, c1, c2 = ancilla_qubits[9:12]

    edges = [
        (0, 1), (1, 2), (1, 3), (1, 4), (2, 4),
        (2, 5), (3, 4), (3, 5), (4, 5),
    ]

    # Compute an edge flag iff both endpoints are absent from the cover.
    for (u, v), flag in zip(edges, edge_flags):
        qc.x(problem_qubits[u])
        qc.x(problem_qubits[v])
        qc.ccx(problem_qubits[u], problem_qubits[v], flag)
        qc.x(problem_qubits[v])
        qc.x(problem_qubits[u])

    # Reversibly add each selected vertex into the 3-bit count register.
    for q in problem_qubits:
        qc.mcx([q, c0, c1], c2)
        qc.ccx(q, c0, c1)
        qc.cx(q, c0)

    # Mark iff every edge flag is zero and the count is at most 3 (c2 == 0).
    for q in edge_flags:
        qc.x(q)
    qc.x(c2)
    qc.h(c2)
    qc.mcx(edge_flags, c2)
    qc.h(c2)
    qc.x(c2)
    for q in reversed(edge_flags):
        qc.x(q)

    # Uncompute the population count.
    for q in reversed(problem_qubits):
        qc.cx(q, c0)
        qc.ccx(q, c0, c1)
        qc.mcx([q, c0, c1], c2)

    # Uncompute edge flags.
    for (u, v), flag in reversed(list(zip(edges, edge_flags))):
        qc.x(problem_qubits[u])
        qc.x(problem_qubits[v])
        qc.ccx(problem_qubits[u], problem_qubits[v], flag)
        qc.x(problem_qubits[v])
        qc.x(problem_qubits[u])
```
