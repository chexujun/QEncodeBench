```python
import math
from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    flags = ancilla_qubits[:5]
    work = ancilla_qubits[5]

    edges = [(0, 2), (1, 2), (2, 3), (2, 4), (3, 4)]
    equal_code_pairs = [(0, 0), (0, 3), (3, 0), (3, 3), (1, 1), (2, 2)]

    def toggle_equal_color(v1, v2, target):
        controls = [
            problem_qubits[2 * v1],
            problem_qubits[2 * v1 + 1],
            problem_qubits[2 * v2],
            problem_qubits[2 * v2 + 1],
        ]

        for c1, c2 in equal_code_pairs:
            expected = [
                c1 & 1,
                (c1 >> 1) & 1,
                c2 & 1,
                (c2 >> 1) & 1,
            ]
            for qubit, bit in zip(controls, expected):
                if bit == 0:
                    qc.x(qubit)

            qc.mcx(controls, target, ancilla_qubits=[work], mode="recursion")

            for qubit, bit in reversed(list(zip(controls, expected))):
                if bit == 0:
                    qc.x(qubit)

    for (u, v), flag in zip(edges, flags):
        qc.x(flag)
        toggle_equal_color(u, v, flag)

    qc.mcp(math.pi, flags[:4], flags[4])

    for (u, v), flag in reversed(list(zip(edges, flags))):
        toggle_equal_color(u, v, flag)
        qc.x(flag)
```
