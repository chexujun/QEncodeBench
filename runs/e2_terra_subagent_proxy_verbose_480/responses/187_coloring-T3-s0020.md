```python
import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    def xor_pattern(controls, values, target):
        for qubit, value in zip(controls, values):
            if value == 0:
                qc.x(qubit)

        if len(controls) == 2:
            qc.ccx(controls[0], controls[1], target)
        else:
            qc.mcx(controls, target)

        for qubit, value in reversed(list(zip(controls, values))):
            if value == 0:
                qc.x(qubit)

    def xor_same_color(u, v, target):
        ul, uh = problem_qubits[2 * u], problem_qubits[2 * u + 1]
        vl, vh = problem_qubits[2 * v], problem_qubits[2 * v + 1]

        # Equality of decoded colors, expressed as an XOR polynomial.
        qc.x(target)
        xor_pattern([ul, uh], [1, 0], target)  # u has color 1
        xor_pattern([ul, uh], [0, 1], target)  # u has color 2
        xor_pattern([vl, vh], [1, 0], target)  # v has color 1
        xor_pattern([vl, vh], [0, 1], target)  # v has color 2
        xor_pattern([ul, uh, vl, vh], [1, 0, 0, 1], target)
        xor_pattern([ul, uh, vl, vh], [0, 1, 1, 0], target)

    def compute_leaf_ok(vertex, target):
        # Given colors(1) != colors(4), this is 1 precisely when vertex
        # has the remaining third color.
        qc.x(target)
        xor_same_color(vertex, 1, target)
        xor_same_color(vertex, 4, target)

    a0, a1, a2, a3 = ancilla_qubits[:4]

    compute_leaf_ok(0, a0)
    compute_leaf_ok(2, a1)
    compute_leaf_ok(3, a2)

    # a3 = 1 iff colors 1 and 4 differ.
    qc.x(a3)
    xor_same_color(1, 4, a3)

    qc.mcp(math.pi, [a0, a1, a2], a3)

    qc.x(a3)
    xor_same_color(1, 4, a3)
    compute_leaf_ok(3, a2)
    compute_leaf_ok(2, a1)
    compute_leaf_ok(0, a0)
```
