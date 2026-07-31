```python
import math
from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    flags = ancilla_qubits[:4]
    phase_ancilla = ancilla_qubits[4]
    edges = [(0, 1), (0, 4), (1, 4), (2, 3)]

    def compute_equal(v1, v2, target):
        l1, h1 = problem_qubits[2 * v1], problem_qubits[2 * v1 + 1]
        l2, h2 = problem_qubits[2 * v2], problem_qubits[2 * v2 + 1]

        # Let p = low XOR high.  The decoded colors are equal iff
        # 1 XOR p1 XOR p2 XOR p1*p2*low1 XOR p1*p2*low2 is one.
        qc.x(target)
        qc.cx(l1, h1)
        qc.cx(l2, h2)
        qc.mcx([h1, h2, l1], target)
        qc.mcx([h1, h2, l2], target)
        qc.cx(l2, h2)
        qc.cx(l1, h1)

    def uncompute_equal(v1, v2, target):
        l1, h1 = problem_qubits[2 * v1], problem_qubits[2 * v1 + 1]
        l2, h2 = problem_qubits[2 * v2], problem_qubits[2 * v2 + 1]

        qc.cx(l1, h1)
        qc.cx(l2, h2)
        qc.mcx([h1, h2, l2], target)
        qc.mcx([h1, h2, l1], target)
        qc.cx(l2, h2)
        qc.cx(l1, h1)
        qc.x(target)

    for edge, flag in zip(edges, flags):
        compute_equal(edge[0], edge[1], flag)

    # Flags are one precisely for monochromatic edges.  Kick back a phase
    # exactly when every flag is zero.
    qc.x(flags)
    qc.x(phase_ancilla)
    qc.h(phase_ancilla)
    qc.mcx(flags, phase_ancilla)
    qc.h(phase_ancilla)
    qc.x(phase_ancilla)
    qc.x(flags)

    for edge, flag in reversed(list(zip(edges, flags))):
        uncompute_equal(edge[0], edge[1], flag)
```
