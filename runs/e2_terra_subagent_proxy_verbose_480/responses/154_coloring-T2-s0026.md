```python
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edge_list = [
        (0, 1), (0, 2), (0, 4), (1, 2),
        (1, 3), (1, 4), (2, 3), (3, 4),
    ]
    edge_flags = ancilla_qubits[:8]
    phase_flag = ancilla_qubits[8]

    def toggle_equal(u: int, v: int, target: int) -> None:
        u0 = problem_qubits[2 * u]
        u1 = problem_qubits[2 * u + 1]
        v0 = problem_qubits[2 * v]
        v1 = problem_qubits[2 * v + 1]

        # Algebraic-normal-form implementation of decoded_color(u) ==
        # decoded_color(v), including the constant term.
        qc.x(target)
        qc.cx(u0, target)
        qc.cx(u1, target)
        qc.cx(v0, target)
        qc.cx(v1, target)
        qc.ccx(u1, v0, target)
        qc.ccx(u0, v1, target)
        qc.mcx([u0, u1, v0], target)
        qc.mcx([u0, u1, v1], target)
        qc.mcx([u0, v0, v1], target)
        qc.mcx([u1, v0, v1], target)

    # Compute one monochromatic-edge flag per edge.
    for (u, v), flag in zip(edge_list, edge_flags):
        toggle_equal(u, v, flag)

    # Convert equality flags to "edge is properly colored" controls.
    for flag in edge_flags:
        qc.x(flag)

    # Apply a phase exactly when every edge is properly colored.
    qc.mcx(edge_flags, phase_flag)
    qc.z(phase_flag)
    qc.mcx(edge_flags, phase_flag)

    for flag in reversed(edge_flags):
        qc.x(flag)

    # Uncompute all edge flags.
    for (u, v), flag in reversed(list(zip(edge_list, edge_flags))):
        toggle_equal(u, v, flag)
```
