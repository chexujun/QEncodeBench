```python
from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    flags = ancilla_qubits[:4]
    phase_ancilla = ancilla_qubits[4]
    edges = ((0, 1), (0, 3), (1, 3), (2, 3))

    def compute_equal(u, v, target):
        ul, uh = problem_qubits[2 * u], problem_qubits[2 * u + 1]
        vl, vh = problem_qubits[2 * v], problem_qubits[2 * v + 1]

        # Form code-bit differences in u's two qubits.
        qc.cx(vl, ul)
        qc.cx(vh, uh)

        # Equal binary codes: differences are 00.
        qc.x(ul)
        qc.x(uh)
        qc.ccx(ul, uh, target)
        qc.x(uh)
        qc.x(ul)

        # The additional decoded-color-0 cases: 00 <-> 11.
        qc.x(vl)
        qc.x(vh)
        qc.mcx([ul, uh, vl, vh], target)
        qc.x(vh)
        qc.x(vl)

        qc.mcx([ul, uh, vl, vh], target)

        # Restore the original code bits.
        qc.cx(vh, uh)
        qc.cx(vl, ul)

    for (u, v), flag in zip(edges, flags):
        compute_equal(u, v, flag)

    # Mark exactly when no edge is monochromatic.
    for flag in flags:
        qc.x(flag)
    qc.mcx(flags, phase_ancilla)
    qc.z(phase_ancilla)
    qc.mcx(flags, phase_ancilla)
    for flag in reversed(flags):
        qc.x(flag)

    for (u, v), flag in reversed(list(zip(edges, flags))):
        compute_equal(u, v, flag)
```
