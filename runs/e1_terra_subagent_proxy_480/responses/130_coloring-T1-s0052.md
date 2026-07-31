```python
from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    def toggle_same_color(u: int, v: int, target: int) -> None:
        u0, u1 = problem_qubits[2 * u], problem_qubits[2 * u + 1]
        v0, v1 = problem_qubits[2 * v], problem_qubits[2 * v + 1]

        # Convert u1 and v1 temporarily to "nonzero-color" flags.
        qc.cx(u0, u1)
        qc.cx(v0, v1)

        # Both decoded colors are zero.
        qc.x(u1)
        qc.x(v1)
        qc.ccx(u1, v1, target)
        qc.x(v1)
        qc.x(u1)

        # Both are nonzero and their distinguishing low bits agree.
        qc.cx(u0, v0)
        qc.x(v0)
        qc.mcx([u1, v1, v0], target)
        qc.x(v0)
        qc.cx(u0, v0)

        qc.cx(v0, v1)
        qc.cx(u0, u1)

    equality_flags = ancilla_qubits[:3]

    for (u, v), flag in zip(((0, 3), (1, 2), (3, 4)), equality_flags):
        toggle_same_color(u, v, flag)

    # Mark exactly when no edge has equal endpoint colors.
    for flag in equality_flags:
        qc.x(flag)
    qc.ccz(*equality_flags)
    for flag in reversed(equality_flags):
        qc.x(flag)

    for (u, v), flag in reversed(
        list(zip(((0, 3), (1, 2), (3, 4)), equality_flags))
    ):
        toggle_same_color(u, v, flag)
```
