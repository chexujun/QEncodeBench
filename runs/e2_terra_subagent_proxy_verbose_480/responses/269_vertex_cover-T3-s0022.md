```python
import math
from qiskit import QuantumCircuit


def build_oracle(
    qc: QuantumCircuit,
    problem_qubits: list[int],
    ancilla_qubits: list[int],
) -> None:
    edge_flags = ancilla_qubits[:6]
    count_bits = ancilla_qubits[6:9]  # little-endian, enough for counts 0..6
    c0, c1, c2 = count_bits

    edges = [(0, 1), (0, 4), (0, 5), (1, 2), (1, 3), (3, 5)]

    # Compute one flag per edge: 1 iff the edge is covered.
    for flag, (u, v) in zip(edge_flags, edges):
        qc.x(flag)
        qc.x(problem_qubits[u])
        qc.x(problem_qubits[v])
        qc.ccx(problem_qubits[u], problem_qubits[v], flag)
        qc.x(problem_qubits[v])
        qc.x(problem_qubits[u])

    # Reversibly add the six selected vertices into a 3-bit counter.
    for vertex in problem_qubits:
        qc.mcx([vertex, c0, c1], c2)
        qc.ccx(vertex, c0, c1)
        qc.cx(vertex, c0)

    # For counts 0..6, c2 == 0 exactly when the cover size is at most 3.
    qc.x(c2)
    qc.mcp(math.pi, edge_flags, c2)
    qc.x(c2)

    # Uncompute the counter.
    for vertex in reversed(problem_qubits):
        qc.cx(vertex, c0)
        qc.ccx(vertex, c0, c1)
        qc.mcx([vertex, c0, c1], c2)

    # Uncompute edge-coverage flags.
    for flag, (u, v) in reversed(list(zip(edge_flags, edges))):
        qc.x(problem_qubits[u])
        qc.x(problem_qubits[v])
        qc.ccx(problem_qubits[u], problem_qubits[v], flag)
        qc.x(problem_qubits[v])
        qc.x(problem_qubits[u])
        qc.x(flag)
```
