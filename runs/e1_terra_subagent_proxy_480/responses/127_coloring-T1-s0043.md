```python
from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    def toggle_equal_color(a0: int, a1: int, b0: int, b1: int, target: int) -> None:
        # Convert the first code into its bitwise difference from the second.
        qc.cx(b0, a0)
        qc.cx(b1, a1)

        # Equal two-bit encodings.
        qc.x(a0)
        qc.x(a1)
        qc.mcx([a0, a1], target)
        qc.x(a1)
        qc.x(a0)

        # The remaining equal-color cases are 00 <-> 11.
        qc.cx(b0, b1)
        qc.x(b1)
        qc.mcx([a0, a1, b1], target)
        qc.x(b1)
        qc.cx(b0, b1)

        qc.cx(b1, a1)
        qc.cx(b0, a0)

    edges = ((0, 2), (0, 3), (1, 3), (2, 3))
    edge_flags = ancilla_qubits[:4]
    phase_qubit = ancilla_qubits[4]

    for (u, v), flag in zip(edges, edge_flags):
        toggle_equal_color(
            problem_qubits[2 * u],
            problem_qubits[2 * u + 1],
            problem_qubits[2 * v],
            problem_qubits[2 * v + 1],
            flag,
        )

    for flag in edge_flags:
        qc.x(flag)
    qc.mcx(edge_flags, phase_qubit)
    qc.z(phase_qubit)
    qc.mcx(edge_flags, phase_qubit)
    for flag in reversed(edge_flags):
        qc.x(flag)

    for (u, v), flag in reversed(list(zip(edges, edge_flags))):
        toggle_equal_color(
            problem_qubits[2 * u],
            problem_qubits[2 * u + 1],
            problem_qubits[2 * v],
            problem_qubits[2 * v + 1],
            flag,
        )
```
