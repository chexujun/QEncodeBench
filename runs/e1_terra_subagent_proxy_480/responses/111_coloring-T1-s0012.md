```python
def build_oracle(qc, problem_qubits, ancilla_qubits) -> None:
    edge_ancillas = ancilla_qubits[:4]
    phase_ancilla = ancilla_qubits[4]
    edges = ((0, 3), (1, 3), (2, 4), (3, 4))

    def equality(a0, a1, b0, b1, target):
        # Toggle target when the two decoded ternary colors are equal.
        # Equal raw encodings, except that 00 and 11 are also equivalent.
        qc.x(a0)
        qc.x(a1)
        qc.x(b0)
        qc.x(b1)
        qc.mcx([a0, a1, b0, b1], target)
        qc.x(a0)
        qc.x(a1)
        qc.x(b0)
        qc.x(b1)

        qc.x(a0)
        qc.x(a1)
        qc.mcx([a0, a1, b0, b1], target)
        qc.x(a0)
        qc.x(a1)

        qc.x(b0)
        qc.x(b1)
        qc.mcx([a0, a1, b0, b1], target)
        qc.x(b0)
        qc.x(b1)

        qc.mcx([a0, a1, b0, b1], target)

        qc.x(a0)
        qc.x(b0)
        qc.mcx([a0, a1, b0, b1], target)
        qc.x(a0)
        qc.x(b0)

        qc.x(a1)
        qc.x(b1)
        qc.mcx([a0, a1, b0, b1], target)
        qc.x(a1)
        qc.x(b1)

    for (u, v), target in zip(edges, edge_ancillas):
        a0, a1 = problem_qubits[2 * u], problem_qubits[2 * u + 1]
        b0, b1 = problem_qubits[2 * v], problem_qubits[2 * v + 1]
        equality(a0, a1, b0, b1, target)
        qc.x(target)

    qc.mcx(edge_ancillas, phase_ancilla)
    qc.z(phase_ancilla)
    qc.mcx(edge_ancillas, phase_ancilla)

    for (u, v), target in reversed(list(zip(edges, edge_ancillas))):
        qc.x(target)
        a0, a1 = problem_qubits[2 * u], problem_qubits[2 * u + 1]
        b0, b1 = problem_qubits[2 * v], problem_qubits[2 * v + 1]
        equality(a0, a1, b0, b1, target)
```
