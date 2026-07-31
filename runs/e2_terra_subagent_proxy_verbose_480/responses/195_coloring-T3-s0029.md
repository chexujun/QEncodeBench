```python
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    flags = ancilla_qubits[:4]
    group_ok = ancilla_qubits[4]

    # Toggle target exactly when the two endpoint codes decode to the same color.
    # Equal decoded colors comprise:
    #   color 0: endpoint codes independently in {00, 11}
    #   color 1: both codes 01
    #   color 2: both codes 10
    def toggle_if_same_color(u, v, target):
        controls = [problem_qubits[2 * u], problem_qubits[2 * u + 1],
                    problem_qubits[2 * v], problem_qubits[2 * v + 1]]
        patterns = (
            (0, 0, 0, 0), (0, 0, 1, 1),
            (1, 1, 0, 0), (1, 1, 1, 1),
            (1, 0, 1, 0), (0, 1, 0, 1),
        )
        for pattern in patterns:
            for qubit, bit in zip(controls, pattern):
                if bit == 0:
                    qc.x(qubit)
            qc.mcx(controls, target)
            for qubit, bit in reversed(list(zip(controls, pattern))):
                if bit == 0:
                    qc.x(qubit)

    def compute_edges(edges):
        for edge, flag in zip(edges, flags):
            toggle_if_same_color(edge[0], edge[1], flag)

    def uncompute_edges(edges):
        for edge, flag in reversed(list(zip(edges, flags))):
            toggle_if_same_color(edge[0], edge[1], flag)

    def toggle_group_ok():
        for flag in flags:
            qc.x(flag)
        qc.mcx(flags, group_ok)
        for flag in flags:
            qc.x(flag)

    first_edges = ((0, 1), (0, 4), (0, 5), (1, 3))
    second_edges = ((1, 5), (2, 3), (3, 4), (4, 5))

    # Compute whether the first four edges are all non-monochromatic.
    compute_edges(first_edges)
    toggle_group_ok()
    uncompute_edges(first_edges)

    # Apply the phase iff group_ok is set and the remaining four flags are zero.
    compute_edges(second_edges)
    for flag in flags:
        qc.x(flag)
    qc.h(flags[3])
    qc.mcx([group_ok, flags[0], flags[1], flags[2]], flags[3])
    qc.h(flags[3])
    for flag in flags:
        qc.x(flag)
    uncompute_edges(second_edges)

    # Clean up the saved first-group predicate.
    compute_edges(first_edges)
    toggle_group_ok()
    uncompute_edges(first_edges)
```
