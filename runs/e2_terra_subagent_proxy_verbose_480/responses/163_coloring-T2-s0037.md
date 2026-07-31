```python
def build_oracle(qc, problem_qubits, ancilla_qubits):
    # The first seven ancillas hold the seven "bad edge" flags.
    # The eighth is used in |-> for phase kickback.
    edge_flags = ancilla_qubits[:7]
    phase_qubit = ancilla_qubits[7]

    edges = (
        (0, 1), (0, 2), (1, 2), (1, 3),
        (1, 4), (2, 3), (3, 4),
    )

    def toggle_equal_color(u, v, target):
        """XOR into target whether decoded colors of u and v are equal."""
        ul, uh = problem_qubits[2 * u], problem_qubits[2 * u + 1]
        vl, vh = problem_qubits[2 * v], problem_qubits[2 * v + 1]

        # Algebraic normal form of decoded_color(u) == decoded_color(v),
        # for variables (ul, uh, vl, vh).  Codes 00 and 11 both mean color 0.
        qc.x(target)
        qc.cx(ul, target)
        qc.cx(uh, target)
        qc.cx(vl, target)
        qc.cx(vh, target)
        qc.ccx(uh, vl, target)
        qc.ccx(ul, vh, target)
        qc.mcx([ul, uh, vl], target)
        qc.mcx([ul, uh, vh], target)
        qc.mcx([ul, vl, vh], target)
        qc.mcx([uh, vl, vh], target)

    # Compute a flag for every monochromatic edge.
    for (u, v), flag in zip(edges, edge_flags):
        toggle_equal_color(u, v, flag)

    # Convert "no bad edges" into all-one controls.
    for flag in edge_flags:
        qc.x(flag)

    # A controlled X on |-> supplies a -1 phase exactly when all flags are 0.
    qc.x(phase_qubit)
    qc.h(phase_qubit)
    qc.mcx(edge_flags, phase_qubit)
    qc.h(phase_qubit)
    qc.x(phase_qubit)

    for flag in edge_flags:
        qc.x(flag)

    # Uncompute all edge flags.
    for (u, v), flag in reversed(list(zip(edges, edge_flags))):
        toggle_equal_color(u, v, flag)
```
