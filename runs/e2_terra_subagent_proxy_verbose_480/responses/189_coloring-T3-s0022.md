```python
import math
from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    flags = ancilla_qubits[:3]

    # Change each vertex encoding from (low, high) to (low, low XOR high).
    # The high bit is now 0 exactly for decoded color 0; when it is 1,
    # the low bit distinguishes colors 1 and 2.
    for vertex in range(5):
        qc.cx(problem_qubits[2 * vertex], problem_qubits[2 * vertex + 1])

    def compute_proper_triangle(vertices, target):
        lows = [problem_qubits[2 * v] for v in vertices]
        parities = [problem_qubits[2 * v + 1] for v in vertices]

        # A triangle is properly 3-colored iff exactly one vertex has
        # parity 0 (color 0), while the other two have different low bits.
        for zero_vertex in range(3):
            others = [index for index in range(3) if index != zero_vertex]
            first, second = others

            # Store low[first] XOR low[second] temporarily in low[second].
            qc.cx(lows[first], lows[second])

            # Turn the required parity pattern (0, 1, 1) into all ones.
            qc.x(parities[zero_vertex])
            qc.mcx(
                [parities[0], parities[1], parities[2], lows[second]],
                target,
            )
            qc.x(parities[zero_vertex])

            qc.cx(lows[first], lows[second])

    # The graph is the union of these three triangles.
    triangles = [(0, 2, 3), (0, 3, 4), (1, 3, 4)]
    for triangle, flag in zip(triangles, flags):
        compute_proper_triangle(triangle, flag)

    # Apply -1 iff every triangle is proper.
    qc.h(flags[2])
    qc.ccx(flags[0], flags[1], flags[2])
    qc.h(flags[2])

    # Uncompute all work bits.
    for triangle, flag in reversed(list(zip(triangles, flags))):
        compute_proper_triangle(triangle, flag)

    for vertex in reversed(range(5)):
        qc.cx(problem_qubits[2 * vertex], problem_qubits[2 * vertex + 1])
```
