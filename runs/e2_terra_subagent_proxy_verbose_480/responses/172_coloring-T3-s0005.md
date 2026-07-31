```python
import math
from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    c0, c1, c2, equal_flag = ancilla_qubits[:4]

    edges = (
        (0, 1),
        (1, 2),
        (1, 3),
        (1, 5),
        (2, 4),
        (2, 5),
        (3, 4),
    )

    def compute_equal(u: int, v: int) -> None:
        ul, uh = problem_qubits[2 * u], problem_qubits[2 * u + 1]
        vl, vh = problem_qubits[2 * v], problem_qubits[2 * v + 1]

        # Change high bits to low XOR high.  It is 0 exactly for decoded
        # color 0, and 1 for decoded colors 1 and 2.
        qc.cx(ul, uh)
        qc.cx(vl, vh)

        # Both decoded colors are 0.
        qc.x(uh)
        qc.x(vh)
        qc.ccx(uh, vh, equal_flag)
        qc.x(vh)
        qc.x(uh)

        # Both are nonzero and equal: either both color 2, or both color 1.
        qc.x(ul)
        qc.x(vl)
        qc.mcx([uh, vh, ul, vl], equal_flag)
        qc.x(vl)
        qc.x(ul)
        qc.mcx([uh, vh, ul, vl], equal_flag)

    def uncompute_equal(u: int, v: int) -> None:
        ul, uh = problem_qubits[2 * u], problem_qubits[2 * u + 1]
        vl, vh = problem_qubits[2 * v], problem_qubits[2 * v + 1]

        qc.mcx([uh, vh, ul, vl], equal_flag)
        qc.x(ul)
        qc.x(vl)
        qc.mcx([uh, vh, ul, vl], equal_flag)
        qc.x(vl)
        qc.x(ul)

        qc.x(uh)
        qc.x(vh)
        qc.ccx(uh, vh, equal_flag)
        qc.x(vh)
        qc.x(uh)

        qc.cx(vl, vh)
        qc.cx(ul, uh)

    def controlled_increment() -> None:
        qc.mcx([equal_flag, c0, c1], c2)
        qc.ccx(equal_flag, c0, c1)
        qc.cx(equal_flag, c0)

    def controlled_decrement() -> None:
        qc.cx(equal_flag, c0)
        qc.ccx(equal_flag, c0, c1)
        qc.mcx([equal_flag, c0, c1], c2)

    # Count monochromatic edges in a 3-bit register.
    for u, v in edges:
        compute_equal(u, v)
        controlled_increment()
        uncompute_equal(u, v)

    # Mark precisely when the count is zero.
    qc.x(c0)
    qc.x(c1)
    qc.x(c2)
    qc.h(c2)
    qc.ccx(c0, c1, c2)
    qc.h(c2)
    qc.x(c2)
    qc.x(c1)
    qc.x(c0)

    # Restore the count register and all temporary workspace.
    for u, v in reversed(edges):
        compute_equal(u, v)
        controlled_decrement()
        uncompute_equal(u, v)
```
