```python
import math
from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    # In every proper coloring, vertices (0, 3, 4) have distinct colors,
    # while vertex 1 has vertex 3's color and vertex 2 has vertex 4's color.
    # Each tuple is (color of {1,3}, color of {2,4}, color of {0}).
    color_cases = (
        (0, 1, 2),
        (0, 2, 1),
        (1, 0, 2),
        (1, 2, 0),
        (2, 0, 1),
        (2, 1, 0),
    )

    for color_13, color_24, color_0 in color_cases:
        colors = (color_0, color_13, color_24, color_13, color_24)

        # A code represents color 0 precisely when its two bits are equal.
        zero_vertices = [v for v, color in enumerate(colors) if color == 0]
        zero_flags = []

        for index, vertex in enumerate(zero_vertices):
            flag = ancilla_qubits[index]
            low = problem_qubits[2 * vertex]
            high = problem_qubits[2 * vertex + 1]
            qc.cx(low, flag)
            qc.cx(high, flag)
            qc.x(flag)  # flag = 1 iff low == high
            zero_flags.append(flag)

        controls = list(zero_flags)
        flipped = []

        # Colors 1 and 2 have their unique binary codes: 01 and 10.
        for vertex, color in enumerate(colors):
            if color == 0:
                continue

            low = problem_qubits[2 * vertex]
            high = problem_qubits[2 * vertex + 1]
            controls.extend((low, high))

            desired_low, desired_high = ((1, 0) if color == 1 else (0, 1))
            if desired_low == 0:
                qc.x(low)
                flipped.append(low)
            if desired_high == 0:
                qc.x(high)
                flipped.append(high)

        phase_target = ancilla_qubits[3]
        qc.x(phase_target)
        qc.mcp(math.pi, controls, phase_target)
        qc.x(phase_target)

        for qubit in reversed(flipped):
            qc.x(qubit)

        for index, vertex in reversed(list(enumerate(zero_vertices))):
            flag = ancilla_qubits[index]
            low = problem_qubits[2 * vertex]
            high = problem_qubits[2 * vertex + 1]
            qc.x(flag)
            qc.cx(high, flag)
            qc.cx(low, flag)
```
