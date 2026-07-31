```python
from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    edge_flags = ancilla_qubits[:5]
    phase_work = ancilla_qubits[5]
    edges = [(0, 4), (1, 2), (1, 4), (2, 3), (2, 4)]

    def compute_equal_flag(u, v, flag):
        u0, u1 = problem_qubits[2 * u], problem_qubits[2 * u + 1]
        v0, v1 = problem_qubits[2 * v], problem_qubits[2 * v + 1]

        # Replace low bits temporarily by parity bits: 0 iff decoded color is 0.
        qc.cx(u1, u0)
        qc.cx(v1, v0)

        # Both decoded colors are 0.
        qc.x(u0)
        qc.x(v0)
        qc.mcx([u0, v0], flag)
        qc.x(v0)
        qc.x(u0)

        # Both are nonzero and have equal high bits:
        # 01 matches 01, or 10 matches 10.
        qc.x(u1)
        qc.x(v1)
        qc.mcx([u0, v0, u1, v1], flag)
        qc.x(v1)
        qc.x(u1)
        qc.mcx([u0, v0, u1, v1], flag)

        qc.cx(v1, v0)
        qc.cx(u1, u0)

    for (u, v), flag in zip(edges, edge_flags):
        compute_equal_flag(u, v, flag)

    # Apply a phase iff no edge is monochromatic.
    for flag in edge_flags:
        qc.x(flag)
    qc.h(phase_work)
    qc.mcx(edge_flags, phase_work)
    qc.h(phase_work)
    for flag in reversed(edge_flags):
        qc.x(flag)

    for (u, v), flag in reversed(list(zip(edges, edge_flags))):
        compute_equal_flag(u, v, flag)
```
