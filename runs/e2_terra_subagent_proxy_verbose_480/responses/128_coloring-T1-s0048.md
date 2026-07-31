```python
from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    flags = ancilla_qubits[:4]
    scratch = ancilla_qubits[4]

    def controlled_toggle(controls, values, target):
        for qubit, value in zip(controls, values):
            if value == 0:
                qc.x(qubit)
        qc.mcx(controls, target)
        for qubit, value in reversed(list(zip(controls, values))):
            if value == 0:
                qc.x(qubit)

    def compute_edge_equal(vertex_a, vertex_b, target):
        a0 = problem_qubits[2 * vertex_a]
        a1 = problem_qubits[2 * vertex_a + 1]
        b0 = problem_qubits[2 * vertex_b]
        b1 = problem_qubits[2 * vertex_b + 1]

        # scratch is 1 precisely when vertex_a has color 0 (code 00 or 11).
        qc.cx(a0, scratch)
        qc.cx(a1, scratch)
        qc.x(scratch)

        # Toggle target when both vertices decode to color 0.
        controlled_toggle([scratch, b0, b1], [1, 0, 0], target)
        controlled_toggle([scratch, b0, b1], [1, 1, 1], target)

        qc.x(scratch)
        qc.cx(a1, scratch)
        qc.cx(a0, scratch)

        # Toggle target when both vertices have color 1 or both have color 2.
        controlled_toggle([a0, a1, b0, b1], [1, 0, 1, 0], target)
        controlled_toggle([a0, a1, b0, b1], [0, 1, 0, 1], target)

    edges = ((0, 1), (0, 2), (0, 3), (1, 2))

    for (u, v), flag in zip(edges, flags):
        compute_edge_equal(u, v, flag)

    # A valid coloring has no monochromatic-edge flags.
    for flag in flags:
        qc.x(flag)
    qc.h(flags[3])
    qc.mcx(flags[:3], flags[3])
    qc.h(flags[3])
    for flag in reversed(flags):
        qc.x(flag)

    for (u, v), flag in reversed(list(zip(edges, flags))):
        compute_edge_equal(u, v, flag)
```
