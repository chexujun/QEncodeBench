```python
from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    edge_flags = ancilla_qubits[:4]
    phase_flag = ancilla_qubits[4]

    def compute_edge_equality(u: int, v: int, target: int) -> None:
        ul, uh = problem_qubits[2 * u], problem_qubits[2 * u + 1]
        vl, vh = problem_qubits[2 * v], problem_qubits[2 * v + 1]

        # Convert low bits to parity bits: p = low XOR high.
        # p = 0 represents decoded color 0 (codes 00 and 11).
        qc.cx(uh, ul)
        qc.cx(vh, vl)

        # Both vertices decode to color 0.
        qc.x(ul)
        qc.x(vl)
        qc.ccx(ul, vl, target)
        qc.x(vl)
        qc.x(ul)

        # For nonzero colors, both parities are 1 and their high bits agree.
        qc.cx(uh, vh)
        qc.x(vh)
        qc.mcx([ul, vl, vh], target)
        qc.x(vh)
        qc.cx(uh, vh)

        # Restore the problem register.
        qc.cx(vh, vl)
        qc.cx(uh, ul)

    edges = [(0, 1), (0, 3), (2, 3), (3, 4)]

    # Compute whether each edge is monochromatic.
    for (u, v), flag in zip(edges, edge_flags):
        compute_edge_equality(u, v, flag)

    # Mark exactly when no edge is monochromatic.
    for flag in edge_flags:
        qc.x(flag)
    qc.mcx(edge_flags, phase_flag)
    qc.z(phase_flag)
    qc.mcx(edge_flags, phase_flag)
    for flag in edge_flags:
        qc.x(flag)

    # Uncompute all edge flags.
    for (u, v), flag in zip(edges, edge_flags):
        compute_edge_equality(u, v, flag)
```
