```python
from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    # One ancilla per edge stores whether its endpoint colors are equal.
    edge_equal = ancilla_qubits[:5]
    phase_flag = ancilla_qubits[5]

    edges = [(0, 2), (1, 2), (1, 3), (1, 4), (3, 4)]

    # Pairs of 2-bit encodings representing equal decoded colors.
    # Codes 00 and 11 both represent color 0.
    equal_patterns = [
        (0, 0, 0, 0),
        (0, 0, 1, 1),
        (1, 1, 0, 0),
        (1, 1, 1, 1),
        (1, 0, 1, 0),  # color 1: 01
        (0, 1, 0, 1),  # color 2: 10
    ]

    def compute_edge_equality(vertex_a: int, vertex_b: int, target: int) -> None:
        controls = [
            problem_qubits[2 * vertex_a],
            problem_qubits[2 * vertex_a + 1],
            problem_qubits[2 * vertex_b],
            problem_qubits[2 * vertex_b + 1],
        ]
        for pattern in equal_patterns:
            for qubit, bit in zip(controls, pattern):
                if bit == 0:
                    qc.x(qubit)
            qc.mcx(controls, target)
            for qubit, bit in reversed(list(zip(controls, pattern))):
                if bit == 0:
                    qc.x(qubit)

    # Compute which edges are monochromatic.
    for (u, v), target in zip(edges, edge_equal):
        compute_edge_equality(u, v, target)

    # Mark exactly when no edge is monochromatic.
    for qubit in edge_equal:
        qc.x(qubit)
    qc.mcx(edge_equal, phase_flag)
    qc.z(phase_flag)
    qc.mcx(edge_equal, phase_flag)
    for qubit in reversed(edge_equal):
        qc.x(qubit)

    # Uncompute all work ancillas.
    for (u, v), target in reversed(list(zip(edges, edge_equal))):
        compute_edge_equality(u, v, target)
```
