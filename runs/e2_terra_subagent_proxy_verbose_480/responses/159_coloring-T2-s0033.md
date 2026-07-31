```python
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = ((0, 1), (0, 3), (1, 3), (2, 3), (2, 4))
    flags = ancilla_qubits[:5]
    phase_ancilla = ancilla_qubits[5]

    def toggle_decoded_equal(u: int, v: int, target: int) -> None:
        u0, u1 = problem_qubits[2 * u], problem_qubits[2 * u + 1]
        v0, v1 = problem_qubits[2 * v], problem_qubits[2 * v + 1]

        # Toggle for identical two-bit codes.
        qc.cx(u0, v0)
        qc.cx(u1, v1)
        qc.x(v0)
        qc.x(v1)
        qc.ccx(v0, v1, target)
        qc.x(v1)
        qc.x(v0)
        qc.cx(u1, v1)
        qc.cx(u0, v0)

        # Additionally toggle for 00 versus 11, since both decode to color 0.
        qc.cx(v0, v1)
        qc.cx(u0, u1)
        qc.cx(u0, v0)
        qc.x(u1)
        qc.x(v1)
        qc.mcx([u1, v1, v0], target)
        qc.x(v1)
        qc.x(u1)
        qc.cx(u0, v0)
        qc.cx(u0, u1)
        qc.cx(v0, v1)

    # Compute one flag per edge: flag = 1 exactly when decoded colors differ.
    for (u, v), flag in zip(edges, flags):
        qc.x(flag)
        toggle_decoded_equal(u, v, flag)

    # Apply the phase exactly when all five edge constraints hold.
    qc.mcx(flags, phase_ancilla)
    qc.z(phase_ancilla)
    qc.mcx(flags, phase_ancilla)

    # Uncompute all edge flags.
    for (u, v), flag in reversed(list(zip(edges, flags))):
        toggle_decoded_equal(u, v, flag)
        qc.x(flag)
```
