```python
from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    a0, a1, a2, a3, a4 = ancilla_qubits

    def pattern_mcx(controls, values, target):
        """Toggle target iff controls equal the specified bit pattern."""
        zero_controls = [q for q, value in zip(controls, values) if value == 0]
        for q in zero_controls:
            qc.x(q)
        qc.mcx(list(controls), target)
        for q in reversed(zero_controls):
            qc.x(q)

    def toggle_equal(v, w, target, prefix=()):
        """
        Toggle target iff decoded colors of vertices v and w are equal,
        additionally conditioned on every prefix qubit being 1.
        """
        lv, hv = problem_qubits[2 * v], problem_qubits[2 * v + 1]
        lw, hw = problem_qubits[2 * w], problem_qubits[2 * w + 1]

        # In this temporary encoding, h=0 means decoded color 0;
        # h=1 together with l=1 means color 1, and l=0 means color 2.
        qc.cx(lv, hv)
        qc.cx(lw, hw)

        p = list(prefix)

        # Both decoded colors are 0.
        pattern_mcx(p + [hv, hw], [1] * len(p) + [0, 0], target)

        # Both decoded colors are 1.
        pattern_mcx(
            p + [lv, hv, lw, hw],
            [1] * len(p) + [1, 1, 1, 1],
            target,
        )

        # Both decoded colors are 2.
        pattern_mcx(
            p + [lv, hv, lw, hw],
            [1] * len(p) + [0, 1, 0, 1],
            target,
        )

        qc.cx(lw, hw)
        qc.cx(lv, hv)

    def compute_good_edge(v, w, target):
        # target <- (decoded_color(v) != decoded_color(w))
        qc.x(target)
        toggle_equal(v, w, target)

    def uncompute_good_edge(v, w, target):
        toggle_equal(v, w, target)
        qc.x(target)

    def toggle_four_good(edges, flags, target):
        """
        Toggle target iff all four supplied edges are properly colored.
        The first three edge predicates occupy flags; the fourth is
        incorporated directly as a condition on target.
        """
        for (v, w), flag in zip(edges[:3], flags):
            compute_good_edge(v, w, flag)

        # First require the first three good-edge flags.
        qc.mcx(list(flags), target)

        # The preceding toggle is cancelled precisely when edge four is
        # monochromatic, leaving target toggled iff edge four is also good.
        toggle_equal(edges[3][0], edges[3][1], target, prefix=flags)

        for (v, w), flag in reversed(list(zip(edges[:3], flags))):
            uncompute_good_edge(v, w, flag)

    first_edges = [(0, 2), (0, 5), (1, 2), (1, 4)]
    second_edges = [(2, 3), (2, 4), (3, 4), (4, 5)]

    # a0 records that the first four constraints all hold.
    toggle_four_good(first_edges, [a1, a2, a3], a0)

    # Record the remaining four constraints, then phase-flip iff all five
    # accumulated conditions are true.
    for (v, w), flag in zip(second_edges, [a1, a2, a3, a4]):
        compute_good_edge(v, w, flag)

    qc.h(a4)
    qc.mcx([a0, a1, a2, a3], a4)
    qc.h(a4)

    for (v, w), flag in reversed(list(zip(second_edges, [a1, a2, a3, a4]))):
        uncompute_good_edge(v, w, flag)

    # Uncompute the first-group conjunction and return all ancillas to zero.
    toggle_four_good(first_edges, [a1, a2, a3], a0)
```
