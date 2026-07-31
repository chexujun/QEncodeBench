```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    edges = [(0, 2), (0, 3), (1, 3), (2, 3)]
    edge_flags = ancilla_qubits[:4]
    phase_ancilla = ancilla_qubits[4]

    def toggle_same_color(target, u, v):
        u0, u1 = problem_qubits[2 * u], problem_qubits[2 * u + 1]
        v0, v1 = problem_qubits[2 * v], problem_qubits[2 * v + 1]

        # Toggle for identical two-bit codes.
        qc.cx(u0, v0)
        qc.x(v0)
        qc.cx(u1, v1)
        qc.x(v1)
        qc.ccx(v0, v1, target)
        qc.x(v1)
        qc.cx(u1, v1)
        qc.x(v0)
        qc.cx(u0, v0)

        # Add the two distinct encodings of color 0: 00 <-> 11.
        for values in ((0, 0, 1, 1), (1, 1, 0, 0)):
            qubits = (u0, u1, v0, v1)
            for qubit, value in zip(qubits, values):
                if value == 0:
                    qc.x(qubit)
            qc.mcx(list(qubits), target)
            for qubit, value in reversed(list(zip(qubits, values))):
                if value == 0:
                    qc.x(qubit)

    for flag, (u, v) in zip(edge_flags, edges):
        toggle_same_color(flag, u, v)

    # Flags are 1 for monochromatic edges.  Flip them so all controls are
    # 1 exactly when every edge has different colors.
    for flag in edge_flags:
        qc.x(flag)
    qc.mcx(edge_flags, phase_ancilla)
    qc.z(phase_ancilla)
    qc.mcx(edge_flags, phase_ancilla)
    for flag in reversed(edge_flags):
        qc.x(flag)

    for flag, (u, v) in reversed(list(zip(edge_flags, edges))):
        toggle_same_color(flag, u, v)
```
