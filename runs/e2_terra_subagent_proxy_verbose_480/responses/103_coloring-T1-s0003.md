```python
from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    # ancilla_qubits[0:4] store whether each graph edge is monochromatic.
    # ancilla_qubits[4] is a temporary phase flag.
    edge_flags = ancilla_qubits[:4]
    phase_flag = ancilla_qubits[4]

    def compute_same_color(a0, a1, b0, b1, target):
        # ANF for decoded-color equality, where 00 and 11 both mean color 0:
        #
        # 1 + a0 + a1 + b0 + b1 + a0*b1 + a1*b0
        #   + a0*b0*b1 + a0*a1*b0 + a1*b0*b1 + a0*a1*b1
        qc.x(target)
        qc.cx(a0, target)
        qc.cx(a1, target)
        qc.cx(b0, target)
        qc.cx(b1, target)
        qc.ccx(a0, b1, target)
        qc.ccx(a1, b0, target)
        qc.mcx([a0, b0, b1], target)
        qc.mcx([a0, a1, b0], target)
        qc.mcx([a1, b0, b1], target)
        qc.mcx([a0, a1, b1], target)

    def uncompute_same_color(a0, a1, b0, b1, target):
        qc.mcx([a0, a1, b1], target)
        qc.mcx([a1, b0, b1], target)
        qc.mcx([a0, a1, b0], target)
        qc.mcx([a0, b0, b1], target)
        qc.ccx(a1, b0, target)
        qc.ccx(a0, b1, target)
        qc.cx(b1, target)
        qc.cx(b0, target)
        qc.cx(a1, target)
        qc.cx(a0, target)
        qc.x(target)

    # Edges: (0,2), (0,3), (1,2), (1,3).
    edges = [(0, 2), (0, 3), (1, 2), (1, 3)]
    for flag, (u, v) in zip(edge_flags, edges):
        compute_same_color(
            problem_qubits[2 * u],
            problem_qubits[2 * u + 1],
            problem_qubits[2 * v],
            problem_qubits[2 * v + 1],
            flag,
        )

    # A valid coloring has no monochromatic edge.
    for flag in edge_flags:
        qc.x(flag)
    qc.mcx(edge_flags, phase_flag)
    qc.z(phase_flag)
    qc.mcx(edge_flags, phase_flag)
    for flag in reversed(edge_flags):
        qc.x(flag)

    for flag, (u, v) in reversed(list(zip(edge_flags, edges))):
        uncompute_same_color(
            problem_qubits[2 * u],
            problem_qubits[2 * u + 1],
            problem_qubits[2 * v],
            problem_qubits[2 * v + 1],
            flag,
        )
```
