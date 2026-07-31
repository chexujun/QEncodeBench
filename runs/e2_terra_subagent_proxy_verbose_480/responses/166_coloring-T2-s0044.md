```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    edge_ancillas = ancilla_qubits[:6]
    phase_ancilla = ancilla_qubits[6]

    def compute_equal(a, b, c, d, target):
        # Equality after decoding 00 and 11 as the same color:
        # 1 + a+b+c+d + a*d + b*c + a*b*c + a*c*d + a*b*d + b*c*d
        qc.x(target)
        qc.cx(a, target)
        qc.cx(b, target)
        qc.cx(c, target)
        qc.cx(d, target)
        qc.ccx(a, d, target)
        qc.ccx(b, c, target)
        qc.mcx([a, b, c], target)
        qc.mcx([a, c, d], target)
        qc.mcx([a, b, d], target)
        qc.mcx([b, c, d], target)

    def uncompute_equal(a, b, c, d, target):
        qc.mcx([b, c, d], target)
        qc.mcx([a, b, d], target)
        qc.mcx([a, c, d], target)
        qc.mcx([a, b, c], target)
        qc.ccx(b, c, target)
        qc.ccx(a, d, target)
        qc.cx(d, target)
        qc.cx(c, target)
        qc.cx(b, target)
        qc.cx(a, target)
        qc.x(target)

    edges = [(0, 2), (0, 3), (0, 4), (1, 2), (1, 4), (3, 4)]

    for (u, v), target in zip(edges, edge_ancillas):
        compute_equal(
            problem_qubits[2 * u], problem_qubits[2 * u + 1],
            problem_qubits[2 * v], problem_qubits[2 * v + 1],
            target,
        )

    for target in edge_ancillas:
        qc.x(target)
    qc.mcx(edge_ancillas, phase_ancilla)
    qc.z(phase_ancilla)
    qc.mcx(edge_ancillas, phase_ancilla)
    for target in reversed(edge_ancillas):
        qc.x(target)

    for (u, v), target in reversed(list(zip(edges, edge_ancillas))):
        uncompute_equal(
            problem_qubits[2 * u], problem_qubits[2 * u + 1],
            problem_qubits[2 * v], problem_qubits[2 * v + 1],
            target,
        )
```
