```python
import math
from qiskit import QuantumCircuit


def build_oracle(qc: QuantumCircuit, problem_qubits: list[int],
                 ancilla_qubits: list[int]) -> None:
    edges = [(0, 1), (0, 4), (1, 2), (2, 3), (2, 4), (3, 4)]
    edge_flags = ancilla_qubits[:6]

    # The four disjoint code-pair cases in which two decoded colors match:
    # 00~00, 11~11, 01~01, 10~10.
    equal_cases = [
        (0, 0, 0, 0),
        (1, 1, 1, 1),
        (1, 0, 1, 0),
        (0, 1, 0, 1),
    ]

    def toggle_equal_flag(v, w, target):
        controls = [
            problem_qubits[2 * v],
            problem_qubits[2 * v + 1],
            problem_qubits[2 * w],
            problem_qubits[2 * w + 1],
        ]

        for pattern in equal_cases:
            zero_controls = [
                controls[i] for i, bit in enumerate(pattern) if bit == 0
            ]
            for qubit in zero_controls:
                qc.x(qubit)
            qc.mcx(controls, target)
            for qubit in reversed(zero_controls):
                qc.x(qubit)

    # Compute whether each edge is monochromatic.
    for (v, w), flag in zip(edges, edge_flags):
        toggle_equal_flag(v, w, flag)

    # Apply -1 exactly when no edge is monochromatic.
    for flag in edge_flags:
        qc.x(flag)
    qc.mcp(math.pi, edge_flags[:-1], edge_flags[-1])
    for flag in reversed(edge_flags):
        qc.x(flag)

    # Uncompute all edge flags.
    for (v, w), flag in reversed(list(zip(edges, edge_flags))):
        toggle_equal_flag(v, w, flag)
```
