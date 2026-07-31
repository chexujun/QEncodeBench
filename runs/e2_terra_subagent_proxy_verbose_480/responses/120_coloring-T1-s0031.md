```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    edge_flags = ancilla_qubits[:4]
    phase_flag = ancilla_qubits[4]

    def compute_same_color(v0, v1, target):
        l0, h0 = problem_qubits[2 * v0], problem_qubits[2 * v0 + 1]
        l1, h1 = problem_qubits[2 * v1], problem_qubits[2 * v1 + 1]

        # Both decode to color 0: each code is either 00 or 11.
        qc.cx(l0, h0)
        qc.cx(l1, h1)
        qc.x(h0)
        qc.x(h1)
        qc.ccx(h0, h1, target)
        qc.x(h1)
        qc.x(h0)
        qc.cx(l1, h1)
        qc.cx(l0, h0)

        # Both are color 1, encoded as 01.
        qc.x(h0)
        qc.x(h1)
        qc.mcx([l0, h0, l1, h1], target)
        qc.x(h1)
        qc.x(h0)

        # Both are color 2, encoded as 10.
        qc.x(l0)
        qc.x(l1)
        qc.mcx([l0, h0, l1, h1], target)
        qc.x(l1)
        qc.x(l0)

    edges = [(0, 1), (0, 2), (1, 3), (2, 3)]

    for (u, v), flag in zip(edges, edge_flags):
        compute_same_color(u, v, flag)

    # phase_flag = 1 exactly when no edge is monochromatic.
    for flag in edge_flags:
        qc.x(flag)
    qc.mcx(edge_flags, phase_flag)
    for flag in reversed(edge_flags):
        qc.x(flag)

    qc.z(phase_flag)

    for flag in edge_flags:
        qc.x(flag)
    qc.mcx(edge_flags, phase_flag)
    for flag in reversed(edge_flags):
        qc.x(flag)

    for (u, v), flag in reversed(list(zip(edges, edge_flags))):
        compute_same_color(u, v, flag)
```
