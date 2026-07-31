```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    edge_flags = ancilla_qubits[:3]

    # These are the 2-bit code pairs that decode to the same color.
    # Bit order is: low(u), high(u), low(v), high(v).
    equal_color_patterns = (
        (0, 0, 0, 0),  # color 0: 00, 00
        (0, 0, 1, 1),  # color 0: 00, 11
        (1, 1, 0, 0),  # color 0: 11, 00
        (1, 1, 1, 1),  # color 0: 11, 11
        (1, 0, 1, 0),  # color 1: 01, 01
        (0, 1, 0, 1),  # color 2: 10, 10
    )

    def toggle_if_pattern(controls, target, pattern):
        for qubit, bit in zip(controls, pattern):
            if bit == 0:
                qc.x(qubit)
        qc.mcx(controls, target)
        for qubit, bit in reversed(list(zip(controls, pattern))):
            if bit == 0:
                qc.x(qubit)

    def compute_edge_violation(u, v, target, reverse=False):
        controls = [
            problem_qubits[2 * u],
            problem_qubits[2 * u + 1],
            problem_qubits[2 * v],
            problem_qubits[2 * v + 1],
        ]
        patterns = reversed(equal_color_patterns) if reverse else equal_color_patterns
        for pattern in patterns:
            toggle_if_pattern(controls, target, pattern)

    edges = ((0, 1), (1, 2), (2, 3))

    for (u, v), flag in zip(edges, edge_flags):
        compute_edge_violation(u, v, flag)

    # Mark states with no monochromatic edge.
    for flag in edge_flags:
        qc.x(flag)
    qc.h(edge_flags[2])
    qc.ccx(edge_flags[0], edge_flags[1], edge_flags[2])
    qc.h(edge_flags[2])
    for flag in reversed(edge_flags):
        qc.x(flag)

    for (u, v), flag in reversed(list(zip(edges, edge_flags))):
        compute_edge_violation(u, v, flag, reverse=True)
```
