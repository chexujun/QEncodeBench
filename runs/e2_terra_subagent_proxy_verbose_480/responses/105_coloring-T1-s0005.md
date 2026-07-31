```python
import math
from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit, problem_qubits: list[int], ancilla_qubits: list[int]
) -> None:
    # The ANF below computes equality of two decoded colors into target:
    # 1 + a0 + a1 + b0 + a1*b0 + a0*a1*b0 + b1
    #   + a0*b1 + a0*a1*b1 + a0*b0*b1 + a1*b0*b1.
    def color_equal(a0, a1, b0, b1, target):
        qc.x(target)
        qc.cx(a0, target)
        qc.cx(a1, target)
        qc.cx(b0, target)
        qc.ccx(a1, b0, target)
        qc.mcx([a0, a1, b0], target)
        qc.cx(b1, target)
        qc.ccx(a0, b1, target)
        qc.mcx([a0, a1, b1], target)
        qc.mcx([a0, b0, b1], target)
        qc.mcx([a1, b0, b1], target)

    def uncompute_color_equal(a0, a1, b0, b1, target):
        qc.mcx([a1, b0, b1], target)
        qc.mcx([a0, b0, b1], target)
        qc.mcx([a0, a1, b1], target)
        qc.ccx(a0, b1, target)
        qc.cx(b1, target)
        qc.mcx([a0, a1, b0], target)
        qc.ccx(a1, b0, target)
        qc.cx(b0, target)
        qc.cx(a1, target)
        qc.cx(a0, target)
        qc.x(target)

    edges = [(0, 1), (0, 3), (2, 4), (3, 4)]
    flags = ancilla_qubits[:4]

    for (u, v), flag in zip(edges, flags):
        color_equal(
            problem_qubits[2 * u],
            problem_qubits[2 * u + 1],
            problem_qubits[2 * v],
            problem_qubits[2 * v + 1],
            flag,
        )

    # Mark precisely when none of the four edges is monochromatic.
    for flag in flags:
        qc.x(flag)
    qc.mcp(math.pi, flags[:3], flags[3])
    for flag in reversed(flags):
        qc.x(flag)

    for (u, v), flag in reversed(list(zip(edges, flags))):
        uncompute_color_equal(
            problem_qubits[2 * u],
            problem_qubits[2 * u + 1],
            problem_qubits[2 * v],
            problem_qubits[2 * v + 1],
            flag,
        )
```
